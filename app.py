from flask import Flask, request, jsonify, render_template, redirect, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# =========================
# CONFIG
# =========================
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///business.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# MODELS
# =========================
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    status = db.Column(db.String(50))

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100))
    content = db.Column(db.Text)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    reply = db.Column(db.Text)

# =========================
# AI CONFIG
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_ai(prompt):
    if not GROQ_API_KEY:
        return "GROQ_API_KEY missing"

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a business AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=20
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"AI Error: {str(e)}"

# =========================
# PAGES
# =========================
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login")
def login_page():
    return render_template("auth.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/crm")
def crm():
    return render_template("crm.html")

@app.route("/email-ai")
def email_ai():
    return render_template("email-ai.html")

@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/ai-chat")
def ai_chat():
    return render_template("ai-chat.html")

# =========================
# LOGIN API
# =========================
@app.route("/login", methods=["POST"])
def login_post():
    return render_template("auth.html")

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if email == "admin@gmail.com" and password == "1234":
        session["user"] = email
        return jsonify({"success": True, "redirect": "/dashboard"})

    return jsonify({"success": False, "message": "Invalid credentials"})

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# =========================
# EMAIL AI
# =========================
@app.route("/generate-email", methods=["POST"])
def generate_email():

    data = request.get_json()
    prompt = data.get("prompt", "")

    email_text = ask_ai(
        f"Write a short professional business email under 150 words:\n{prompt}"
    )

    db.session.add(Email(email=email_text))
    db.session.commit()

    return jsonify({"email": email_text})

# =========================
# LEADS
# =========================
@app.route("/save-lead", methods=["POST"])
def save_lead():

    data = request.get_json()

    db.session.add(Lead(
        name=data.get("name"),
        company=data.get("company"),
        status=data.get("status", "New")
    ))

    db.session.commit()

    return jsonify({"message": "Lead saved"})

@app.route("/get-leads")
def get_leads():

    leads = Lead.query.order_by(Lead.id.desc()).all()

    return jsonify({
        "leads": [
            {
                "id": l.id,
                "name": l.name,
                "company": l.company,
                "status": l.status
            }
            for l in leads
        ]
    })

# =========================
# REPORTS
# =========================
@app.route("/generate-report", methods=["POST"])
def generate_report():

    data = request.get_json()
    topic = data.get("topic", "")

    report = ask_ai(
        f"Write a detailed business report on: {topic}"
    )

    db.session.add(Report(
        type=topic,
        content=report
    ))

    db.session.commit()

    return jsonify({"report": report})


@app.route("/get-reports")
def get_reports():

    reports = Report.query.order_by(Report.id.desc()).all()

    return jsonify({
        "reports": [
            {
                "id": r.id,
                "type": r.type,
                "content": r.content
            }
            for r in reports
        ]
    })

# =========================
# CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    msg = data.get("message")

    reply = ask_ai(msg)

    db.session.add(ChatHistory(
        message=msg,
        reply=reply
    ))

    db.session.commit()

    return jsonify({"reply": reply})

# =========================
# STATS
# =========================
@app.route("/stats")
def stats():

    return jsonify({
        "emails": Email.query.count(),
        "leads": Lead.query.count(),
        "reports": Report.query.count(),
        "chats": ChatHistory.query.count()
    })

# =========================
# INIT DB
# =========================
with app.app_context():
    db.create_all()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)