import os
import faiss
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import google.generativeai as genai

# --- Load Environment Variables ---
load_dotenv()

# --- Initialize Local Models and Pipelines ---
sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model="distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True
)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Google Gemini API Setup ---
# This is the new, more reliable setup
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
    # --- MODIFIED: Updated the model name to the stable version ---
    gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')
except Exception as e:
    print(f"Error configuring Google Gemini: {e}")
    gemini_model = None

# --- Knowledge Base (RAG) Setup ---
def setup_knowledge_base():
    try:
        with open('kb.txt', 'r', encoding='utf-8') as f:
            kb_content = f.read().split('Q:')[1:]
        
        questions = [item.split('A:')[0].strip() for item in kb_content]
        answers = [item.split('A:')[1].strip() for item in kb_content]
        question_embeddings = embedding_model.encode(questions)
        
        index = faiss.IndexFlatL2(question_embeddings.shape[1])
        index.add(np.array(question_embeddings, dtype=np.float32))
        
        return index, questions, answers
    except FileNotFoundError:
        return None, [], []

kb_index, kb_questions, kb_answers = setup_knowledge_base()

# --- Main AI Functions ---
def analyze_priority(text: str) -> str:
    text_lower = text.lower()
    urgent_keywords = ['urgent', 'critical', 'immediately', 'down', 'cannot access', 'billing error']
    if any(keyword in text_lower for keyword in urgent_keywords):
        return "Urgent"
    return "Not Urgent"

def analyze_sentiment(text: str) -> str:
    results = sentiment_pipeline(text)
    return results[0]['label'].capitalize()

def find_relevant_context(query: str, top_k=2):
    if kb_index is None:
        return "No knowledge base found."
    query_embedding = embedding_model.encode([query])
    _, indices = kb_index.search(np.array(query_embedding, dtype=np.float32), top_k)
    context = ""
    for i in indices[0]:
        context += f"Q: {kb_questions[i]}\nA: {kb_answers[i]}\n\n"
    return context

# --- MODIFIED: This function now uses the Google Gemini API ---
def generate_draft_reply(email_body: str, sender_sentiment: str) -> str:
    if gemini_model is None:
        return "AI model is not configured. Please check your Google API key."

    context = find_relevant_context(email_body)
    
    prompt = f"""You are a friendly and professional customer support assistant.
A customer has sent an email with a '{sender_sentiment}' sentiment.

Here is the customer's email:
"{email_body}"

Here is some relevant information from our knowledge base that might help answer their question:
Context:
"{context}"

Based on the customer's email and the provided context, please draft an empathetic and helpful reply. If the context is not relevant, simply answer based on the email content.
"""
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An exception occurred in generate_draft_reply with Gemini: {e}")
        return "I am sorry, but I was unable to generate a response at this time. A human agent will get back to you shortly."

