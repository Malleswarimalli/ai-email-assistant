# 📧 AI-Powered Email Communication Assistant

An intelligent, end-to-end solution designed to **automate and streamline the management of customer support emails**.
This application leverages the power of **Large Language Models** to analyze, prioritize, and draft responses, transforming your inbox into an efficient, automated command center.

---

## 🎥 Demonstration Video

📹 Watch a full walkthrough of the application's features and workflow here:

\[INSERT YOUR YOUTUBE OR LOOM VIDEO LINK HERE]

---

## ✨ Key Features

### 📨 Automated Email Ingestion

* Automatically fetches all support-related emails from a **Gmail account** over the last 24 hours.
* Searches for keywords like **"Support," "Query," and "Help"** in the entire message.

### 🤖 Intelligent AI Analysis

* **Priority Detection**: A rule-based system instantly flags emails containing keywords like **"Urgent"** or **"Critical"** for immediate attention.
* **Sentiment Analysis**: Uses `distilbert-base-uncased` from Hugging Face to classify tone as **Positive, Negative, or Neutral**.

### ✍️ Context-Aware Response Generation

* Employs the **Google Gemini API (`gemini-1.5-flash-latest`)** to generate high-quality, empathetic, and professional draft replies.
* Features a **RAG pipeline**, using a local `kb.txt` knowledge base to provide factually accurate answers.

### 📊 Interactive Analytics Dashboard

* **At-a-glance statistics** with cards for: Total Emails, Pending, Resolved, and Urgent.
* Charts for **Status Overview, Priority Breakdown, and Sentiment Distribution** over time.

### 🔄 Full End-to-End Workflow

* Review, edit, and send **AI-generated replies** directly from the dashboard.
* Automatically marks the email as **"Resolved"** once sent.

---

## 🏩 Architecture & How It Works

The application operates on a **decoupled client-server architecture**, ensuring scalability and maintainability.

### **Frontend (Client)**

* Built with **HTML, Tailwind CSS, and Chart.js**.
* A clean, responsive **SPA** that communicates with the backend via REST APIs.

### **Backend (API Server)**

* **FastAPI** powers the central brain of the system.
* Exposes endpoints for **fetching emails, generating responses, sending replies, and retrieving analytics**.

### **Email Ingestion Pipeline**

1. Background task triggered via API call.
2. Secure Gmail API connection with **OAuth 2.0**.
3. Fetches and parses all relevant emails.
4. Cleans and stores them in an **SQLite database**.

### **AI Processing Core**

* **Initial Analysis**: Each email is analyzed for priority and sentiment.
* **RAG Pipeline**:

  * Email → Embedding via `SentenceTransformer`.
  * **Faiss** retrieves most relevant context from knowledge base.
  * Combined prompt sent to **Google Gemini API** for draft generation.

### **Database**

* **SQLite** stores all email metadata, AI analysis results, and status (**Pending/Resolved**).

---

## 🛠️ Tech Stack

| Category            | Technology / Service                                    |
| ------------------- | ------------------------------------------------------- |
| **Backend**         | Python, FastAPI                                         |
| **Frontend**        | HTML, Tailwind CSS, Chart.js                            |
| **AI - Generation** | Google Gemini API (`gemini-2.5-flash-lite`)           |
| **AI - Analysis**   | Hugging Face Transformers, Sentence-Transformers, Faiss |
| **Database**        | SQLite                                                  |
| **Email Service**   | Gmail API                                               |

---

## 🚀 Getting Started

Follow these instructions to set up and run the project locally.

### ✅ Prerequisites

* **Python 3.9+**
* A **Google account with Gmail API enabled**
* A **Google Gemini API key**

---

### ⚡ Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME
```

#### 2. Create and Activate a Virtual Environment

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Credentials & API Keys

* **Gmail API**: Enable the Gmail API, download your `credentials.json`, and place it in the project root.
* **Environment Variables**: Create a `.env` file in the root and add your Gemini API key:

```env
GOOGLE_API_KEY="AIzaSy..."
```

---

### ▶️ Run the Application

Start the **FastAPI backend server**:

```bash
uvicorn main:app --reload
```

---

✅ Now your **AI-Powered Email Communication Assistant** is up and running!

---
