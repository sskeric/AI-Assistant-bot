from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import smtplib
from email.mime.text import MIMEText
import os
from google import genai
import datetime
from dotenv import load_dotenv

# load_dotenv returns True if it finds a .env file, False otherwise
if not load_dotenv():
    print("Warning: No .env file found. System environment variables will be used.")

# =========================
# EMAIL MAP
# =========================
EMAIL_MAP = {
    "Hardware": ["a@gmail.com", "b@gmail.com"], # type the correct received email
    "Software": ["c@gmail.com"]
}

# =========================
# Gemini AI Client
# =========================
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# =========================
# Flask Setup
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# Load FAQ
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "..", "data", "faq.json")
BASE_LOG_DIR = os.path.join(BASE_DIR, "..", "incident_logs")

with open(file_path, "r") as f:
    faq_data = json.load(f)

# =========================
# LOGGING FUNCTION (FIXED)
# =========================
def log_chat(message, result, source):
    os.makedirs("incident_logs", exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    log_data = {
        "timestamp": timestamp,
        "message": message,
        "source": source,
        "result": result
    }

    file_path = os.path.join(BASE_LOG_DIR, f"chat_{timestamp}.json")

    with open(file_path, "w") as f:
        json.dump(log_data, f, indent=4)

# =========================
# CLASSIFY ISSUE
# =========================
def classify_issue(message):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"""
Classify ONLY as one word:
Hardware or Software.

Message: {message}

Return only Hardware or Software.
"""
    )

    return response.text.strip().replace(".", "").title()

# =========================
# GENERATE EMAIL TEXT
# =========================
def generate_email(issue_type, message):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"""
Write a short professional email.

To: {issue_type} support team

Problem: {message}
"""
    )
    return response.text.strip()

# =========================
# SEND EMAIL (REAL)
# =========================
def send_email(issue_type, message, body):
    recipients = EMAIL_MAP.get(issue_type, [])

    if not recipients:
        print("No recipients found for:", issue_type)
        return

    msg = MIMEText(body)
    msg["Subject"] = f"[{issue_type}] Support Ticket"
    msg["From"] = "yourgmail@gmail.com"
    msg["To"] = ", ".join(recipients)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        EMAIL_USER = os.getenv("EMAIL_USER")
        EMAIL_PASS = os.getenv("EMAIL_PASS")
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(msg["From"], recipients, msg.as_string())
        server.quit()
    except Exception as e:
        print("Email error:", e)

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "Backend is running!"

# =========================
# CHAT ROUTE (FIXED LOGIC)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data["message"].lower().strip()

    # =========================
    # 1. FAQ CHECK (FIXED)
    # =========================
    for item in faq_data:
        if item["question"].lower() in message:
            result = item["answer"]

            log_chat(message, result, "faq")

            return jsonify({
                "reply": result,
                "source": "faq"
            })

    # =========================
    # 2. AI PROCESS
    # =========================
    issue_type = classify_issue(message)

    # CLEAN OUTPUT (VERY IMPORTANT FIX)
    issue_type = issue_type.replace(".", "").strip().title()

    email_body = generate_email(issue_type, message)

    # =========================
    # 3. SEND EMAIL (REAL)
    # =========================
    send_email(issue_type, message, email_body)

    result = {
        "issue_type": issue_type,
        "email": email_body,
        "status": "sent"
    }

    # =========================
    # 4. LOG
    # =========================
    log_chat(message, result, "ai")

    return jsonify({
        "reply": f"Issue classified as {issue_type}. Email sent.",
        "email": email_body,
        "source": "ai"
    })

# =========================
# TEST AI
# =========================
@app.route("/test-ai", methods=["POST"])
def test_ai():
    data = request.json
    result = classify_issue(data["message"])
    return jsonify({"type": result})

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)