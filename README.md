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
1. User submits a message (create a user from this code "user_id = "exampleabc_user")
2. System checks FAQ database
3. If match → return predefined solution
4. If no match → AI classifies issue (Hardware / Software / Network)
5. AI generates email response (simulation mode)
6. Conversation is logged into /incident_logs/


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
Output:
Classified as: Hardware
AI-generated email response
Log file created

Case 2 (FAQ Matching)  
Input: screen is black  
Output:
Answer: Check the power cable
No AI processing needed


# 🎯 Project Outcome
+ This project demonstrates:
+ AI integration using external APIs
+ Real-time user interaction via web interface
+ Automated issue classification
+ File-based logging system
+ Full-stack development with React (frontend) and Flask (backend)


# Video Demonstration
https://youtu.be/_Gsym3Gxlv4


