# Video Demonstration
https://youtu.be/_Gsym3Gxlv4

# 🤖 Smart-Assist AI Support Bot 
A Flask-based AI chatbot designed as a first-line IT support system.
It provides instant troubleshooting using FAQ matching and AI-powered classification, while automatically logging incidents for review.


# ✨ Features
* Chat interface (React frontend)
* AI issue classification (Hardware / Software / Network)
* FAQ-based instant troubleshooting
* AI-generated email response (simulation mode)
* Automatic incident logging (JSON format)
* RESTful API (Flask backend)


# 🛠 Tech Stack
+ Frontend: React (JavaScript)
+ Backend: Flask (Python)
+ AI Integration: Google Gemini API
+ Data Storage: MySQL + JSON logs
+ Version Control: GitHub


# 🔄 System Workflow
1. User submits an IT support request. The system associates the request with the current application user.
2. System performs FAQ matching using the available FAQ knowledge base.
3. If a relevant FAQ is found, the corresponding solution is returned.
4. If no suitable FAQ is identified, AI is used to classify the issue and generate support assistance.
5. AI generates email response (simulation mode)
6. Incident information may be recorded according to the application's logging configuration.


# 🔒 Security
1. API keys and credentials stored in backend/.env (excluded from GitHub)
2. .env.example provided as a safe template for collaborators
3. No sensitive credentials exposed in code
4. Email system runs in simulation mode (no real sending unless configured)


# ⚙️ Setup Instructions
a. Install Requirements
Make sure you have installed:
+ Node.js
+ Python 3
+ MySQL
+ (Optional) Java JDK if using Gemini SDK locally

b. Get Gemini API Key
1. Go to Google AI Studio
2. Generate an API key
3. Copy the key

c. Configure Environment Variables
1. Inside the backend/ folder:
2. Copy .env.example → rename to .env
3. Fill in your own values (API key, DB credentials, email account)
    Example (Powershell/Terminal): cp backend/.env.example backend/.env

d. Run Backend
- cd backend > python app.py

e. Run Frontend
- cd frontend > npm install   # only needed first time > npm start


# 📝 Notes
+ If .env is missing → AI features will not work (only FAQ responses available)
+ Emails are simulated unless you configure a real Gmail app password
+ Logs are stored in /incident_logs/ (ignored by Git, safe to delete anytime)


# 💡 Example Usage
Case 1 (AI Processing)  
Input: My laptop is overheating
Workflow:
No suitable FAQ match found
- AI classifies the issue
- Support email draft generated
- Incident report created
- Result: Category = Hardware

Case 2 (FAQ Matching)  
Input: screen is black  
Workflow:
- FAQ match identified
- Predefined troubleshooting solution returned
- Result: Check the power cable and monitor connection.


# 🎯 Project Outcome/Demostrate
+ Semantic FAQ matching
+ AI-assisted IT incident classification
+ Automated support email generation
+ Incident tracking and logging
+ Full-stack application development using React (frontend) and Flask (backend)
+ Integration with Google Gemini API
