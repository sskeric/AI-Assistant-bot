🤖 Smart-Assist AI Support Bot
A Flask-based AI chatbot designed as a first-line IT support system.
It provides instant troubleshooting using FAQ matching and AI-powered classification, while automatically logging incidents for review.

✨ Features
Chat interface (React frontend)

AI issue classification (Hardware / Software / Network)

FAQ-based instant troubleshooting

AI-generated email response (simulation mode)

Automatic incident logging (JSON format)

RESTful API (Flask backend)

🛠 Tech Stack
Frontend: React (JavaScript)

Backend: Flask (Python)

AI Integration: Google Gemini API

Data Storage: MySQL + JSON logs

Version Control: GitHub

🔄 System Workflow
User submits a message

System checks FAQ database

If match → return predefined solution

If no match → AI classifies issue (Hardware / Software / Network)

AI generates email response (simulation mode)

Conversation is logged into /incident_logs/

🔒 Security
API keys and credentials stored in backend/.env (excluded from GitHub)

.env.example provided as a safe template for collaborators

No sensitive credentials exposed in code

Email system runs in simulation mode (no real sending unless configured)

⚙️ Setup Instructions
1. Install Requirements
Make sure you have installed:

Node.js

Python 3

MySQL

(Optional) Java JDK if using Gemini SDK locally

2. Get Gemini API Key
Go to Google AI Studio

Generate an API key

Copy the key

3. Configure Environment Variables
Inside the backend/ folder:

Copy .env.example → rename to .env

Fill in your own values (API key, DB credentials, email account)

Example:

bash
cp backend/.env.example backend/.env
4. Run Backend
bash
cd backend
python app.py
5. Run Frontend
bash
cd frontend
npm install   # only needed first time
npm start
📝 Notes
If .env is missing → AI features will not work (only FAQ responses available)

Emails are simulated unless you configure a real Gmail app password

Logs are stored in /incident_logs/ (ignored by Git, safe to delete anytime)

💡 Example Usage
Case 1 (AI Processing)  
Input: My laptop is overheating  
Output:

Classified as: Hardware

AI-generated email response

Log file created

Case 2 (FAQ Matching)  
Input: screen is black  
Output:

Answer: Check the power cable

No AI processing needed

🎯 Project Outcome
This project demonstrates:

AI integration using external APIs

Real-time user interaction via web interface

Automated issue classification

File-based logging system

Full-stack development with React (frontend) and Flask (backend)
