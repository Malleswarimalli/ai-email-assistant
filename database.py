from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./emails.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    # --- THIS IS THE MISSING COLUMN ---
    # It stores the unique ID from Gmail to prevent duplicates.
    message_id = Column(String, unique=True, index=True) 
    
    sender = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    received_at = Column(DateTime)
    sentiment = Column(String)
    priority = Column(String)
    status = Column(String, default='pending')

