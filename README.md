# 🛡️ Multimodal Fake Detection & Verification System

## 📌 Project Overview

The **Multimodal Fake Detection & Verification System** is an AI-powered, all-in-one digital verification platform designed to detect and analyze suspicious, fraudulent, misleading, spam, phishing, and manipulated digital content. The system provides multiple verification modules through a single modern dashboard, allowing users to analyze SMS and email spam, phishing URLs, fake news, social media profiles, phone numbers, fake IDs and certificates, images, audio, and videos. After analyzing the provided input, the system generates a **Risk Score from 0 to 100**, classifies the content according to its risk level, identifies suspicious indicators, provides an explanation, and gives actionable security advice. The platform also maintains scan history using SQLite, provides voice-based feedback through the Web Speech API, uses RAG-based retrieval for news verification, supports optional local LLM integration through Ollama, and allows users to generate professional forensic-style PDF reports.

---

# ✨ Key Features

## 1. 🔍 Multimodal Analysis — All-in-One

The system provides multiple verification modules within a single platform:

- 📩 SMS / Text Spam Detection
- 📧 Email Spam / Phishing Detection
- 🔗 Phishing URL Detection
- 📞 Phone Risk Analysis
- 👤 Social Media Profile Verification
- 📰 Fake News / Content Verification
- 🖼️ Image Deepfake Detection
- 🎥 Video Deepfake Detection
- 🎙️ Audio Deepfake Detection
- 🪪 Fake ID / Certificate Verification

Users can select the required module from the dashboard and provide the corresponding input for analysis.

---

## 2. 🎯 Real-Time Risk Scoring

After every analysis, the system generates a **Risk Score between 0 and 100**.

### Risk Classification

| Risk Score | Result |
|------------|--------|
| 🟢 0–30 | Safe / Low Risk |
| 🟡 31–60 | Medium Risk / Suspicious |
| 🔴 61–100 | High Risk / Potential Fraud |

The risk score is displayed through an interactive visual **Risk Ring** so that users can understand the result quickly.

> The risk score is a system-generated assessment and should be treated as decision-support information rather than absolute proof of authenticity.

---

## 3. 🗣️ Voice Output & Accessibility

The system uses the browser's **Web Speech API** to provide voice feedback.

After the analysis is completed, the system can automatically speak the result and recommended action.

Example:

> "Analysis complete. The result is High Risk. Advice: Do not click the suspicious link."

This makes the application more interactive and improves accessibility for users.

---

## 4. 💡 Actionable Security Advice

The system does not only classify content as safe or suspicious. It also provides practical recommendations to help users respond to potential threats.

Examples include:

- Block the suspicious sender.
- Do not click suspicious links.
- Do not share OTPs or passwords.
- Verify information through trusted sources.
- Report suspicious social media accounts.
- Avoid sharing sensitive personal information.

This makes the system more useful as a security awareness and decision-support platform.

---

## 5. 📰 RAG-Based News Verification

The News Verification module uses a **Retrieval-Augmented Generation (RAG)** approach to verify news claims.

The system converts the user-provided claim into a vector representation using **Sentence-Transformers** and searches for relevant factual information using **ChromaDB**.

### RAG Workflow

```text
User News Claim
       ↓
Text Processing
       ↓
Sentence-Transformers
       ↓
Vector Embedding
       ↓
ChromaDB Vector Search
       ↓
Relevant Factual Evidence
       ↓
Claim & Evidence Comparison
       ↓
Verification Result

This allows the system to compare claims with relevant stored factual information instead of relying only on keyword matching.

6. 🤖 Ollama Local LLM Integration

The system supports optional Ollama integration for running Large Language Models locally.

The LLM can assist the system in generating:

Scam explanations
Phishing explanations
Threat explanations
Analysis summaries
User-friendly recommendations
Actionable security advice

Using Ollama provides the option to use a locally hosted LLM instead of depending completely on external cloud-based AI APIs.

7. 💾 Scan History & Database Persistence

Every completed scan can be stored in a local SQLite database.

The system maintains information such as:

Scan type
Analysis result
Risk score
Classification
Threat indicators
Advice
Timestamp

Users can access their previous scans from the Scan History section.

Database Flow
User Scan
    ↓
FastAPI Backend
    ↓
SQLAlchemy ORM
    ↓
SQLite Database
    ↓
ScanHistory
    ↓
Scan History Dashboard
8. 📄 Forensic PDF Reports

The system provides a professional report-generation feature.

After completing an analysis, users can click Export Forensics Report.

A report preview appears in a modal window, and the report can then be converted into a PDF using html2pdf.js.

The report may contain:

Scan Type
Analysis Date and Time
Risk Score
Classification
Threat Indicators
Explanation
Actionable Advice
Analysis Details
Report Generation Flow
Analysis Result
       ↓
Report Preview
       ↓
html2pdf.js
       ↓
PDF Generation
       ↓
Download
9. 🔎 Visual Threat Indicators / XAI

The system highlights suspicious words, phrases, and patterns detected during analysis.

Examples:

URGENT
FREE MONEY
CLICK NOW
VERIFY ACCOUNT
WINNER
LIMITED TIME

These indicators help users understand why the system considered the content suspicious rather than displaying only a final classification.

This provides a basic Explainable AI (XAI) experience.

🎨 Frontend Technologies
HTML5 & CSS3

Used for the core structure, layout, styling, and responsive user interface.

JavaScript — Vanilla JS

Vanilla JavaScript is used instead of heavy frameworks such as React or Angular.

It handles:

Single Page Application-style logic
DOM manipulation
User interactions
Module switching
Form handling
API requests
Dynamic result rendering
Frontend/backend communication
Tailwind CSS

Used to create the modern user interface, including:

Premium dark theme
Responsive layout
Utility-based styling
Animations
Modern dashboard components
FontAwesome

Used for dashboard icons, navigation icons, status indicators, and other UI elements.

html2pdf.js

Used to convert the report interface into a downloadable PDF directly from the browser.

Web Speech API

Used for browser-based voice output and accessibility.

⚙️ Backend Technologies
Python 3.x

Python is the primary backend programming language used for the application and verification logic.

FastAPI

FastAPI is used to build the REST APIs that connect the frontend with the backend verification engine.

Example API routes include:

/api/analyze/text
/api/analyze/url
/api/history
Uvicorn

Uvicorn is used as the ASGI server to run the FastAPI application locally.

SQLAlchemy

SQLAlchemy is used as the ORM for interacting with the database, creating tables, and performing database operations safely.

SQLite

SQLite is used as a lightweight local database for storing scan history, risk scores, classifications, and advice.

Pydantic

Pydantic is used for request and response data validation to ensure that data received by the backend follows the expected structure.

🧠 AI & Verification Technologies
ChromaDB

ChromaDB is used as the vector database for the RAG-based news and factual verification engine.

Sentence-Transformers

Sentence-Transformers converts text into vector embeddings so that semantically relevant information can be retrieved from ChromaDB.

Ollama

Ollama provides optional local Large Language Model integration for generating explanations and recommendations.

Pillow (PIL)

Pillow is used for image processing and reading image file information in the image/deepfake analysis module.

NLP & Pattern Analysis

The system can analyze text for:

Suspicious keywords
Scam patterns
Urgency-based language
Phishing structures
Fraud-related phrases
Suspicious requests
🏗️ System Architecture

The project follows a Decoupled Client-Server API Architecture.

The frontend and backend run separately and communicate through REST APIs using JavaScript Fetch/AJAX.

┌──────────────────────────────────────────────┐
│                  FRONTEND                    │
│                                              │
│ HTML5 + CSS3                                 │
│ Vanilla JavaScript                           │
│ Tailwind CSS                                 │
│ FontAwesome                                  │
│ html2pdf.js                                  │
│ Web Speech API                               │
└───────────────────────┬──────────────────────┘
                        │
                   Fetch / AJAX
                        │
                        ▼
┌──────────────────────────────────────────────┐
│                   BACKEND                    │
│                                              │
│ Python 3.x                                   │
│ FastAPI                                      │
│ Uvicorn                                      │
│ Pydantic                                     │
│ SQLAlchemy                                   │
└───────────────┬────────────────┬─────────────┘
                │                │
                ▼                ▼
       ┌────────────────┐   ┌─────────────────────┐
       │ SQLite         │   │ AI & Verification   │
       │                │   │ Engine              │
       │ Scan History   │   │                     │
       │ Risk Scores    │   │ ChromaDB            │
       │ Advice         │   │ Sentence-Transformers│
       └────────────────┘   │ Ollama              │
                            │ Pillow              │
                            └─────────────────────┘
Server Configuration
Frontend
http.server → Port 8080


Backend
Uvicorn → Port 8000

The two components communicate through AJAX/Fetch REST API requests.

⚙️ Complete Working Flow
Step 1 — Dashboard Login

The user activates/logs into the system.

After successful access, a premium dark-themed command center dashboard is displayed.

The dashboard contains:

Navigation sidebar
Verification modules
Analysis panel
Risk indicator
Scan history
Report generation
System status

A voice greeting can also be provided through the Web Speech API.

Step 2 — Module Selection & Input

The user selects the required verification module from the left sidebar.

For example:

SMS & Text Spam
Phishing URL
Email Spam / Phishing
Phone Risk
Social Media Profile
News Verification
Image Deepfake
Certificate / ID
Audio Deepfake
Video Deepfake

The user then provides the required input.

Depending on the selected module, the input can be:

Suspicious text
Email content
URL
Phone number
Social media profile information
News claim
Image
ID/certificate
Audio
Video

The user then clicks:

Analyze Content
Step 3 — Backend Processing

The frontend sends the input to the FastAPI backend.

User Input
     ↓
Frontend JavaScript
     ↓
Fetch / AJAX Request
     ↓
FastAPI Backend
     ↓
Verification Engine
Text / URL Analysis

For text-based inputs, the backend checks:

Hidden patterns
Scam keywords
Suspicious phrases
Phishing structures
Fraud-related patterns
Text / URL
     ↓
Preprocessing
     ↓
Pattern Analysis
     ↓
Threat Indicators
     ↓
Risk Calculation
Image / Media Analysis

For image and media inputs, the system can inspect:

File information
Metadata / EXIF information
Image characteristics
Manipulation indicators
Suspicious media patterns
Media Upload
     ↓
File Processing
     ↓
Metadata Analysis
     ↓
Manipulation Indicators
     ↓
Risk Assessment
News Verification

The News Verification module uses the RAG engine.

News Claim
     ↓
Sentence-Transformers
     ↓
Vector Embedding
     ↓
ChromaDB Retrieval
     ↓
Relevant Factual Evidence
     ↓
Claim Comparison
     ↓
Verification Result
Step 4 — Result Calculation & Saving

After completing the analysis, the backend generates:

Risk Score
Classification
Threat Indicators
Explanation
Actionable Advice
Timestamp

Example:

Risk Score: 87 / 100


Classification:
High Risk


Threat Indicators:
• Urgency-based language
• Suspicious request
• Potential phishing pattern


Advice:
Do not click the link or share personal information.

The result is then stored in the SQLite database through SQLAlchemy.

The scan history is maintained in the ScanHistory table.

Step 5 — Frontend Rendering & Feedback

The result is dynamically displayed on the dashboard.

The interface shows:

Animated Risk Ring
Risk Score
Classification
Threat Indicators
Explanation
Actionable Advice

The Risk Ring uses visual indicators for different risk levels.

The voice engine can automatically announce the result.

Example:

"Analysis complete. The result is High Risk. Advice: Do not click the suspicious link."

Step 6 — Exporting the Report

If the user wants a record of the analysis, they can click:

Export Forensics Report

A modal window opens with a report preview.

The report is converted into a PDF using html2pdf.js.

Analysis Result
      ↓
Forensics Report Preview
      ↓
html2pdf.js
      ↓
PDF Report
      ↓
Download
🔌 REST API Architecture

The frontend communicates with the backend through REST APIs.

Typical endpoints include:

POST /api/analyze/text
POST /api/analyze/url
POST /api/analyze/email
POST /api/analyze/phone
POST /api/analyze/social
POST /api/analyze/news
POST /api/analyze/image
POST /api/analyze/document
POST /api/analyze/audio
POST /api/analyze/video


GET /api/history
GET /api/history/{id}

The exact endpoints may vary depending on the final implementation.

📂 Project Structure
AI-verfication-system/
│
├── backend/
│   ├── database.py
│   ├── main.py
│   ├── migrate.py
│   ├── rag_engine.py
│   └── requirements.txt
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
│
├── .gitignore
└── README.md
⚡ Installation & Setup
1. Clone the Repository
git clone https://github.com/EnshaDevi/AI-verfication-system.git
cd AI-verfication-system
2. Create a Virtual Environment
Windows
python -m venv .venv
.venv\Scripts\activate
Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
pip install -r backend/requirements.txt
▶️ Run the Backend

From the project root:

uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

Backend:

http://127.0.0.1:8000

FastAPI interactive API documentation:

http://127.0.0.1:8000/docs
▶️ Run the Frontend

Open another terminal:

cd frontend
python -m http.server 8080

Then open:

http://127.0.0.1:8080
Application Architecture
Frontend → Port 8080
Backend  → Port 8000
🤖 Ollama Configuration

Ollama is an optional component for local LLM-based explanations.

When configured, the flow is:

FastAPI Backend
      ↓
Ollama
      ↓
Local LLM
      ↓
AI Explanation
      ↓
Frontend Result

The system can use the local model to generate human-readable explanations and recommendations.

🧪 Example Test Inputs
Safe SMS
Your OTP is 482913. Do not share it with anyone.

Possible result:

Low Risk / Safe
Suspicious SMS
URGENT! Congratulations! You have won a huge cash prize.
Click now to claim your reward.

Possible result:

High Risk / Spam
Suspicious URL
https://g00gle-security-login.example.com/verify

Possible result:

High Risk / Suspicious
Normal URL
https://www.google.com/

Possible result:

Low Risk

These examples are for demonstration/testing purposes. Actual results depend on the implemented detection logic, models, rules, and available reference data.

🔐 Security & Privacy

For production deployment, the following security practices are recommended:

Validate all uploaded files.
Restrict file upload sizes.
Sanitize user inputs.
Keep API keys and secrets outside the source code.
Use environment variables for sensitive configuration.
Never commit .env files.
Avoid storing sensitive personal documents unnecessarily.
Use HTTPS in production.
Implement authentication and authorization.
Protect administrative endpoints.
Add API rate limiting.
Secure database access.
Treat AI predictions as probabilistic assessments.
🚀 Future Enhancements

Future versions of the system can include:

🔐 Advanced authentication
👨‍💼 Admin analytics dashboard
🌐 Real-time web-based fact verification
🧠 Transformer-based detection models
🎯 Improved model confidence calibration
🖼️ Deepfake localization and heatmaps
🎥 Frame-level video analysis
🎙️ Advanced AI-generated voice detection
📱 Mobile application
☁️ Cloud deployment
🚨 Real-time fraud alerts
📊 Advanced analytics
📧 Automated email scanning
🔗 Threat intelligence integration
🧪 Automated model evaluation
📡 Production monitoring and API rate limiting
🎯 Project Objectives

The main objectives of this project are:

Build a centralized multimodal verification platform.
Detect different types of suspicious digital content.
Generate real-time risk scores.
Identify and highlight suspicious indicators.
Provide understandable explanations.
Give actionable security recommendations.
Verify news claims using RAG-based retrieval.
Maintain persistent scan history.
Generate professional PDF reports.
Improve accessibility through voice output.
Provide a modern and user-friendly security dashboard.

🌟 Why This Project?
Digital threats are no longer limited to traditional spam messages. Users can encounter phishing URLs, fraudulent emails, fake news, manipulated images, deepfake videos, AI-generated audio, fake documents, and suspicious social media accounts.
The Multimodal Fake Detection & Verification System addresses this challenge by bringing multiple verification capabilities into a single AI-powered platform. Instead of providing only a simple Fake/Real result, the system provides a complete analysis containing a Risk Score, Classification, Threat Indicators, Explanation, Actionable Advice, Scan History, Voice Feedback, and PDF Report.
One Dashboard. Multiple Threats. AI-Powered Verification.

🛠️ Technology Stack
Frontend
├── HTML5
├── CSS3
├── Vanilla JavaScript
├── Tailwind CSS
├── FontAwesome
├── html2pdf.js
└── Web Speech API


B
