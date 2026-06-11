import socket

from flask import Flask, abort, request, jsonify
from flask_cors import CORS
import json
import smtplib
from email.mime.text import MIMEText
import os
from google import genai
import datetime
import mysql.connector
from google.genai import errors
import re

# =========================
# Flask Setup
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# Gemini AI Client
# =========================
client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

user_id = "local_user4"

# =========================
# EMAIL MAP
# =========================
EMAIL_MAP = {
    "Hardware": [os.getenv("EMAIL_HARDWARE")],
    "Software": [os.getenv("EMAIL_SOFTWARE")],
    "Network": [os.getenv("EMAIL_NETWORK1"), os.getenv("EMAIL_NETWORK2")]
}

# =========================
# MySQL Connection
# =========================
def get_db_connection():
    try:
        return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )
    except mysql.connector.Error as e:
        print("❌ Database error:", e)
        return None

# =========================
# FAQ CHECK (MySQL)
# =========================
def check_faq(message):
    db = get_db_connection()
    if db is None:
        print("❌ Database connection failed in check_faq()")
        return None

    try:
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT answer FROM faq WHERE LOWER(question) = %s", (message.lower(),))
        result = cur.fetchone()
        return result["answer"] if result else None

    except mysql.connector.Error as e:
        print("❌ Database query error in check_faq():", e)
        return None

    finally:
        if db.is_connected():
            cur.close()
            db.close()

# =========================
# LOGGING SETUP
# =========================

BASE_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "incident_logs")

def log_chat(message, result, source):
    os.makedirs(BASE_LOG_DIR, exist_ok=True)
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
# SPAM CHECK
# =========================
def check_spam(user_id):
    db = get_db_connection()
    if db is None:
        print("❌ Database connection failed in check_spam()")
        return False

    try:
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT spam_count, blocked_until FROM spam_logs WHERE user_id=%s", (user_id,))
        row = cur.fetchone()

        if row and row.get("blocked_until"):
            if datetime.datetime.now() < row["blocked_until"]:
                return True
        return False

    except mysql.connector.Error as e:
        print("❌ Database query error in check_spam():", e)
        return False

    finally:
        if db.is_connected():
            cur.close()
            db.close()

# =========================
# CHECK SUBMMISSION  
# =========================
def check_submission_lock(user_id):
    db = get_db_connection()
    if db is None:
        print("❌ Database connection failed in check_submission_lock()")
        return False

    try:
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT submitted_until FROM spam_logs WHERE user_id=%s", (user_id,))
        row = cur.fetchone()

        if row and row.get("submitted_until"):
            return datetime.datetime.now() < row["submitted_until"]
        return False

    except mysql.connector.Error as e:
        print("❌ Database query error in check_submission_lock():", e)
        return False

    finally:
        if db.is_connected():
            cur.close()
            db.close()

# =========================
# CLASSIFY ISSUE
# =========================
def is_nonsense(text):
    text = text.lower().strip()

    if len(text) < 4:
        return True

    if text in ["hi", "hello", "test", "asd", "qwe", "123"]:
        return True

    if re.fullmatch(r"(asd|qwe|zxc|asdf)+", text):
        return True

    return False

def classify_issue(message):
    # Short-circuit obvious junk
    if not message or len(message.strip()) < 3:
        return "Unknown"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"""
You are an IT support classifier.

ONLY return ONE of these categories:

Hardware
Software
Network
Unknown

Rules:
- Hardware = monitor, keyboard, CPU, RAM, screen, laptop, power issues
- Software = apps, lag, crashes, bugs, browser issues
- Network = wifi, internet, connection issues
- Unknown = nonsense/spam/random text

Examples:
"My PC has blue screen" -> Hardware
"Game runs slow" -> Software
"Internet not working" -> Network
"asdasd" -> Unknown

Message: {message}
"""
        )

        result = response.text.strip()

        # normalize
        if "unknown" in result.lower():
            return "Unknown"
        return result

    except errors.ClientError as e:
        err_msg = str(e)

            # Invalid API key
        if "API key not valid" in err_msg or "API_KEY_INVALID" in err_msg:
            return "InvalidAPIKey"

        # Quota exceeded
        if "RESOURCE_EXHAUSTED" in err_msg:
            return "QuotaExceeded"

        # Service unavailable / maintenance
        if "UNAVAILABLE" in err_msg:
            return "ServiceUnavailable"

        return "Unknown"

    except Exception as e:
        print("Unexpected Gemini error:", type(e).__name__, e)
        return "Unknown"

# =========================
# GENERATE EMAIL TEXT
# =========================
def generate_email(issue_type, message, user_id):
    return f"""
Dear {issue_type} Support Team,

A user ({user_id}) reported the following issue:

{message}

Please investigate this issue.

Regards,
Smart Assist AI
"""

# =========================
# SEND EMAIL (REAL)
# =========================
def send_email(issue_type, body):
    recipients = EMAIL_MAP.get(issue_type, [])

    if not recipients:
        print("No recipients found for:", issue_type)
        return

    msg = MIMEText(body)
    msg["Subject"] = f"[{issue_type}] Support Ticket"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = ", ".join(recipients)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS")) # your own email and then your own google app password
        server.sendmail(msg["From"], recipients, msg.as_string())
        server.quit()
        return "✅ Email successfully sent."
    except smtplib.SMTPAuthenticationError:
        return "❌ Email authentication failed (wrong password or hacked account)."
    except (smtplib.SMTPConnectError, socket.gaierror, ConnectionRefusedError, TimeoutError):
        return "❌ Network error: cannot reach email server."
    except smtplib.SMTPRecipientsRefused:
        return "❌ Recipient email does not exist or was rejected."
    except Exception as e:
        return f"❌ Email error: {e}"    

# =========================
# CHAT ROUTE 
# =========================

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").lower().strip()

    # =========================
    # 1. INIT MODE (SAFE DB)
    # =========================
    if data.get("init"):
        db = get_db_connection()
        faqs = []

        if db is None:
            return jsonify({"reply": "❌ Database unavailable.", "options": ["Other"]})

        try:
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT question FROM faq LIMIT 5")
            faqs = [row["question"] for row in cur.fetchall()]

        except mysql.connector.Error as e:
            print("❌ FAQ init DB error:", e)
            return jsonify({"reply": "❌ Database error loading FAQs.", "options": ["Other"]})

        finally:
            try:
                if db.is_connected():
                    cur.close()
                    db.close()
            except:
                pass

        faqs.append("Other")
        return jsonify({"options": faqs})

    # =========================
    # 2. FAQ CHECK
    # =========================
    faq_answer = check_faq(message)
    if faq_answer:
        log_chat(message, faq_answer, "faq")
        return jsonify({"reply": faq_answer, "source": "faq"})

    # =========================
    # 3. BLOCK CHECKS (SAFE)
    # =========================
    try:
        if check_spam(user_id):
            return jsonify({"reply": "🚫 You are blocked for 24 hours due to spam."})

        if check_submission_lock(user_id):
            return jsonify({"reply": "⏳ You already submitted a request. Please wait 72 hours."})
    except Exception as e:
        print("⚠️ Spam/lock check failed:", e)

    # =========================
    # 4. MAIN AI CLASSIFICATION
    # =========================
    try:
        issue_type = "Unknown" if is_nonsense(message) else classify_issue(message)

        # Gemini errors
        if issue_type == "InvalidAPIKey":
            return jsonify({"reply": "❌ Gemini API key invalid."})
        if issue_type == "QuotaExceeded":
            return jsonify({"reply": "⚠️ Gemini quota exceeded."})
        if issue_type == "ServiceUnavailable":
            return jsonify({"reply": "⚠️ Gemini service unavailable."})

        # =========================
        # 5. VALID ISSUE FLOW (DB SAFE)
        # =========================
        if issue_type != "Unknown":
            db = get_db_connection()
            if db is None:
                return jsonify({"reply": "❌ Database unavailable (cannot log ticket)."})

            try:
                cur = db.cursor(dictionary=True)

                cur.execute("SELECT user_id FROM spam_logs WHERE user_id=%s", (user_id,))
                row = cur.fetchone()

                submitted_until = datetime.datetime.now() + datetime.timedelta(hours=72)

                if row:
                    cur.execute("""
                        UPDATE spam_logs
                        SET spam_count=0,
                            blocked_until=NULL,
                            submitted_until=%s
                        WHERE user_id=%s
                    """, (submitted_until, user_id))
                else:
                    cur.execute("""
                        INSERT INTO spam_logs(user_id, spam_count, blocked_until, submitted_until)
                        VALUES(%s, %s, %s, %s)
                    """, (user_id, 0, None, submitted_until))

                db.commit()

            except mysql.connector.Error as e:
                print("❌ DB error (valid issue flow):", e)
                return jsonify({"reply": "❌ Database error while saving ticket."})

            finally:
                try:
                    if db.is_connected():
                        cur.close()
                        db.close()
                except:
                    pass

            # Email + logging (outside DB risk)
            email_body = generate_email(issue_type, message, user_id)
            email_status = send_email(issue_type, email_body)

            log_chat(message, issue_type, "ai")

            return jsonify({
                "reply": f"Issue classified as {issue_type}. {email_status}",
                "source": "ai"
            })

        # =========================
        # 6. UNKNOWN (SPAM FLOW SAFE)
        # =========================
        db = get_db_connection()
        if db is None:
            return jsonify({"reply": "❌ Database unavailable."})

        try:
            cur = db.cursor(dictionary=True)

            cur.execute("SELECT spam_count FROM spam_logs WHERE user_id=%s", (user_id,))
            row = cur.fetchone()

            spam_count = (row["spam_count"] + 1) if row else 1

            if spam_count >= 3:
                cur.execute("""
                    UPDATE spam_logs
                    SET spam_count=%s, blocked_until=%s
                    WHERE user_id=%s
                """, (
                    spam_count,
                    datetime.datetime.now() + datetime.timedelta(hours=24),
                    user_id
                ))
                db.commit()
                return jsonify({"reply": "🚫 Blocked for 24 hours due to spam."})

            if row:
                cur.execute(
                    "UPDATE spam_logs SET spam_count=%s WHERE user_id=%s",
                    (spam_count, user_id)
                )
            else:
                cur.execute(
                    "INSERT INTO spam_logs(user_id, spam_count) VALUES(%s, %s)",
                    (user_id, 1)
                )

            db.commit()

        except mysql.connector.Error as e:
            print("❌ DB error (spam flow):", e)
            return jsonify({"reply": "❌ Database error during spam tracking."})

        finally:
            try:
                if db.is_connected():
                    cur.close()
                    db.close()
            except:
                pass

        return jsonify({
            "reply": f"Warning {spam_count}/3: Please type a proper message."
        })

    # =========================
    # 7. GLOBAL ERROR HANDLER
    # =========================
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"reply": "Internal server error."}), 500
    
# =========================
# HOME
# =========================
@app.route("/")
def home():
    db = get_db_connection()
    if db is None:
        return "❌ Database error: Cannot connect to MySQL."
    return "Backend is running!"
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