import os
import base64
from datetime import datetime, timedelta
import pytz
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from database import SessionLocal, engine, Email as EmailDB, Base
from ai_processor import analyze_priority, analyze_sentiment, generate_draft_reply

# --- App Initialization ---
Base.metadata.create_all(bind=engine)
app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Gmail API Setup ---
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('gmail', 'v1', credentials=creds)

# --- Pydantic Models ---
class ReplyRequest(BaseModel):
    reply_text: str

# --- Helper Functions ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_email_body(msg_parts):
    if msg_parts:
        for part in msg_parts:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', 'ignore')
            elif part['mimeType'] == 'multipart/alternative':
                return get_email_body(part.get('parts'))
    return ""

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Email Communication Assistant API"}

@app.post("/fetch-emails/")
def fetch_and_store_emails(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    def task():
        try:
            # --- MODIFIED: The query now searches the entire email, not just the subject. ---
            query = "(Support OR Query OR Request OR Help) newer_than:1d"
            print(f"Searching Gmail with query: {query}")
            
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            # --- THIS IS THE FIX ---
            # It loops through all pages of results from the Gmail API.
            page_count = 1
            while 'nextPageToken' in results:
                page_token = results['nextPageToken']
                print(f"Fetching page {page_count + 1}...")
                results = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
                messages.extend(results.get('messages', []))
                page_count += 1

            print(f"Found a total of {len(messages)} matching emails.")

            if not messages:
                return

            new_email_count = 0
            for message in messages:
                existing_email = db.query(EmailDB).filter(EmailDB.message_id == message['id']).first()
                if existing_email:
                    continue

                new_email_count += 1
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
                date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                
                body = get_email_body(payload.get('parts')) or base64.urlsafe_b64decode(payload.get('body', {}).get('data', '')).decode('utf-8', 'ignore')
                
                try:
                    # More robust date parsing
                    parsed_date = datetime.strptime(date_str.split(' (')[0].strip(), '%a, %d %b %Y %H:%M:%S %z')
                    date_obj = parsed_date.astimezone(pytz.utc)
                except (ValueError, TypeError):
                    date_obj = datetime.now(pytz.utc)

                email_obj = EmailDB(
                    message_id=message['id'],
                    sender=sender,
                    subject=subject,
                    body=body.strip(),
                    received_at=date_obj,
                    priority=analyze_priority(subject + " " + body),
                    sentiment=analyze_sentiment(body),
                    status='pending'
                )
                db.add(email_obj)
            
            if new_email_count > 0:
                db.commit()
            print(f"Successfully stored {new_email_count} new emails.")
        except Exception as e:
            print(f"An error occurred during email fetching: {e}")

    background_tasks.add_task(task)
    return {"message": "Email fetching process started in the background."}

@app.get("/emails/", response_model=list[dict])
def get_emails(db: Session = Depends(get_db)):
    emails = db.query(EmailDB).filter(EmailDB.status == 'pending').order_by(EmailDB.priority.desc(), EmailDB.received_at.desc()).all()
    return [
        {
            "id": e.id, "sender": e.sender, "subject": e.subject, "body": e.body,
            "received_at": e.received_at, "priority": e.priority, "sentiment": e.sentiment
        }
        for e in emails
    ]

@app.post("/emails/{email_id}/generate-response")
def get_draft_reply(email_id: int, db: Session = Depends(get_db)):
    email = db.query(EmailDB).filter(EmailDB.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    draft = generate_draft_reply(email.body, email.sentiment)
    return {"draft_reply": draft}

@app.post("/emails/{email_id}/send")
def send_email_reply(email_id: int, request: ReplyRequest, db: Session = Depends(get_db)):
    email = db.query(EmailDB).filter(EmailDB.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    original_msg = service.users().messages().get(userId='me', id=email.message_id).execute()
    original_headers = original_msg['payload']['headers']
    subject = next((h['value'] for h in original_headers if h['name'].lower() == 'subject'), '')
    to_email = next((h['value'] for h in original_headers if h['name'].lower() == 'from'), '')
    msg_id = next((h['value'] for h in original_headers if h['name'].lower() == 'message-id'), '')

    reply_subject = f"Re: {subject}" if not subject.lower().startswith("re:") else subject
    
    message = f"From: me\nTo: {to_email}\nSubject: {reply_subject}\nIn-Reply-To: {msg_id}\nReferences: {msg_id}\n\n{request.reply_text}"
    raw_message = base64.urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")
    
    try:
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        email.status = 'resolved'
        db.commit()
        return {"message": "Reply sent and email marked as resolved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    one_day_ago = datetime.now(pytz.utc) - timedelta(days=1)
    
    total = db.query(EmailDB).filter(EmailDB.received_at >= one_day_ago).count()
    pending = db.query(EmailDB).filter(EmailDB.status == 'pending').count()
    resolved = db.query(EmailDB).filter(EmailDB.status == 'resolved', EmailDB.received_at >= one_day_ago).count()
    urgent = db.query(EmailDB).filter(EmailDB.status == 'pending', EmailDB.priority == 'Urgent').count()
    
    sentiments = db.query(EmailDB.sentiment).filter(EmailDB.received_at >= one_day_ago).all()
    sentiment_counts = {}
    if sentiments:
        unique_sentiments = {s[0] for s in sentiments if s[0] is not None}
        sentiment_counts = {s: 0 for s in unique_sentiments}
        for s in sentiments:
            if s[0] is not None:
                sentiment_counts[s[0]] += 1

    return {
        "total": total,
        "pending": pending,
        "resolved": resolved,
        "urgent": urgent,
        "sentiment_counts": sentiment_counts
    }

