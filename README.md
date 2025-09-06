📧 AI-Powered Email Communication Assistant
An intelligent, end-to-end solution designed to automate and streamline the management of customer support emails. This application leverages the power of Large Language Models to analyze, prioritize, and draft responses, transforming your inbox into an efficient, automated command center.

🎥 Demonstration Video
Watch a full walkthrough of the application's features and workflow here:

[INSERT YOUR YOUTUBE OR LOOM VIDEO LINK HERE]

✨ Key Features
📨 Automated Email Ingestion: Automatically fetches all support-related emails from a Gmail account over the last 24 hours, searching for keywords like "Support," "Query," and "Help" in the entire message.

🤖 Intelligent AI Analysis:

Priority Detection: A rule-based system instantly flags emails containing keywords like "Urgent" or "Critical" for immediate attention.

Sentiment Analysis: Utilizes a distilbert-base-uncased model from Hugging Face to classify each email's tone as Positive, Negative, or Neutral.

✍️ Context-Aware Response Generation:

Employs the Google Gemini API (gemini-1.5-flash-latest) to generate high-quality, empathetic, and professional draft replies.

Features a Retrieval-Augmented Generation (RAG) pipeline, using a local knowledge base (kb.txt) to find relevant information and provide factually accurate answers.

📊 Interactive Analytics Dashboard:

Provides at-a-glance statistics with cards for Total Emails, Pending, Resolved, and Urgent.

Includes a suite of charts to visualize Status Overview, Priority Breakdown, and Sentiment Distribution over time.

🔄 Full End-to-End Workflow: Allows users to seamlessly review, edit, and send AI-generated replies directly from the dashboard, automatically marking the email as "Resolved".

🏛️ Architecture & How It Works
The application operates on a decoupled client-server architecture, ensuring a scalable and maintainable system.

Frontend (Client): A single-page application built with HTML, Tailwind CSS, and Chart.js. It provides a clean and responsive user interface that communicates with the backend via REST API calls to fetch data and trigger actions.

Backend (API Server): A robust FastAPI server acts as the central brain. It exposes endpoints for fetching emails, generating responses, sending replies, and retrieving analytics data.

Email Ingestion Pipeline:

A background task is initiated via an API call.

It securely connects to the Gmail API using OAuth 2.0 credentials.

It performs a comprehensive search for relevant emails and loops through all pages of results to ensure no email is missed.

Each unique email is parsed, cleaned, and stored in the SQLite database.

AI Processing Core:

Initial Analysis: As soon as an email is stored, it's passed through local AI models for priority and sentiment analysis.

RAG Pipeline for Response Generation:

The user selects an email, triggering a request to the /generate-response endpoint.

The email body is converted into a numerical vector (embedding) using a SentenceTransformer model.

Faiss (Facebook AI Similarity Search) is used to perform an ultra-fast search against a pre-indexed vector knowledge base, retrieving the most relevant Q&A pairs.

This retrieved context is combined with the original email and its sentiment into a carefully engineered prompt.

The final prompt is sent to the Google Gemini API, which returns a coherent, context-aware, and helpful draft reply.

Database: A simple and efficient SQLite database stores all email data, including metadata, AI analysis results, and status (pending/resolved).

🛠️ Tech Stack
Category

Technology / Service

Backend

Python, FastAPI

Frontend

HTML, Tailwind CSS, Chart.js

AI - Generation

Google Gemini API (gemini-1.5-flash-latest)

AI - Analysis

Hugging Face Transformers, Sentence-Transformers, Faiss

Database

SQLite

Email Service

Gmail API

🚀 Getting Started
Follow these instructions to set up and run the project on your local machine.

Prerequisites
Python 3.9+

A Google account with the Gmail API enabled.

A Google Gemini API key.

Installation
Clone the Repository

git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME

Create and Activate a Virtual Environment

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Configure Credentials & API Keys

Gmail API: Follow the Google instructions to enable the Gmail API and download your credentials.json file. Place it in the root of the project folder.

Environment Variables: Create a file named .env in the root of the project and add your Google Gemini API key:

GOOGLE_API_KEY="AIzaSy..."

Run the Application

Start the Backend Server:

uvicorn main:app --reload
