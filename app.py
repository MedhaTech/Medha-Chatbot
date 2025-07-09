from flask import Flask, request, jsonify, send_from_directory, render_template_string, g
from werkzeug.utils import secure_filename
import requests
import os
import sqlite3
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Load data.txt as context
with open('data.txt', 'r', encoding='utf-8') as f:
    DATA_CONTEXT = f.read()

# Load environment variables from .env
load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@medhatech.in')
MIRA_EMAIL = os.getenv('MIRA_EMAIL', 'mira@medhatech.in')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GEMINI_API_KEY

DATABASE = 'support_queries.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'txt', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper to send email

def send_html_email(to_email, subject, html_content, from_email=None):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email or MIRA_EMAIL
    msg['To'] = to_email
    part = MIMEText(html_content, 'html')
    msg.attach(part)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(msg['From'], [to_email], msg.as_string())

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS support_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            category TEXT,
            description TEXT NOT NULL,
            file_path TEXT,
            progress TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

init_db()

@app.route('/')
def index():
    return render_template_string(open('chat_ui.html').read())

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Prepare prompt for Gemini
    prompt = f"""
You are Mira, a helpful assistant bot for Medha Tech Pvt Ltd. Answer the user's question based ONLY on the following context. If the answer is not in the context, politely say you don't know.

Context:
{DATA_CONTEXT}

User: {user_message}
Mira:"""

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to get response from Gemini API'}), 500
    data = response.json()
    try:
        bot_reply = data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        import traceback
        print("Error:", e)
        traceback.print_exc()
        bot_reply = "Sorry, I couldn't process your request."
    return jsonify({'reply': bot_reply})

@app.route('/submit_query', methods=['POST'])
def submit_query():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    category = request.form.get('category')
    description = request.form.get('description')
    file = request.files.get('file')
    progress = request.form.get('progress', 'Open')
    file_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
    db = get_db()
    db.execute('''INSERT INTO support_queries (name, email, phone, category, description, file_path, progress)
                  VALUES (?, ?, ?, ?, ?, ?, ?)''',
               (name, email, phone, category, description, file_path, progress))
    db.commit()

    # Send confirmation email to user
    user_subject = "We've received your support request!"
    user_html = f"""
    <div style='font-family:Roboto,Arial,sans-serif;background:#f6f8fa;padding:0;margin:0;'>
      <table width='100%' bgcolor='#f6f8fa' cellpadding='0' cellspacing='0' style='padding:0;margin:0;'>
        <tr><td align='center'>
          <table width='100%' style='max-width:520px;background:#fff;border-radius:14px;box-shadow:0 2px 16px #0002;margin:32px 0 24px 0;padding:0 0 32px 0;'>
            <tr>
              <td style='background:#F72534;border-radius:14px 14px 0 0;padding:32px 0 18px 0;text-align:center;'>
                <img src='https://cdn-icons-png.flaticon.com/512/4712/4712035.png' alt='Mira Bot' width='56' height='56' style='border-radius:50%;background:#fff;padding:6px 6px 2px 6px;box-shadow:0 2px 8px #0001;'>
                <h1 style='color:#fff;font-size:2rem;margin:18px 0 0 0;font-weight:800;letter-spacing:1px;'>Medha Tech Support</h1>
              </td>
            </tr>
            <tr><td style='padding:32px 32px 0 32px;'>
              <h2 style='color:#F72534;font-size:1.3rem;margin-bottom:8px;'>Hi {name},</h2>
              <p style='font-size:1.08rem;color:#222;margin:0 0 18px 0;'>Thank you for reaching out to <b>Medha Tech</b> support. We've received your request and our team will contact you as soon as possible.</p>
              <div style='background:#f6f8fa;border-radius:8px;padding:18px 18px 12px 18px;margin:18px 0 24px 0;'>
                <h3 style='color:#F72534;font-size:1.08rem;margin:0 0 10px 0;'>Your Query Details</h3>
                <table style='width:100%;font-size:1.01rem;color:#222;'>
                  <tr><td style='padding:4px 0;'><b>Name:</b></td><td>{name}</td></tr>
                  <tr><td style='padding:4px 0;'><b>Email:</b></td><td>{email}</td></tr>
                  <tr><td style='padding:4px 0;'><b>Phone:</b></td><td>{phone}</td></tr>
                  <tr><td style='padding:4px 0;'><b>Category:</b></td><td>{category or 'N/A'}</td></tr>
                  <tr><td style='padding:4px 0;vertical-align:top;'><b>Description:</b></td><td>{description}</td></tr>
                </table>
              </div>
              <p style='color:#444;font-size:1.04rem;margin:0 0 18px 0;'>If you have any further questions, simply reply to this email. We're here to help!</p>
            </td></tr>
            <tr><td style='padding:0 32px;'>
              <hr style='border:none;border-top:1.5px solid #f3f3f3;margin:24px 0;'>
              <p style='color:#888;font-size:0.98rem;text-align:center;'>This is an automated message from <b>Mira Bot</b> 🤖<br>Medha Tech Solutions Pvt. Ltd.<br><a href='https://medhatech.in' style='color:#F72534;text-decoration:none;'>medhatech.in</a></p>
            </td></tr>
          </table>
        </td></tr>
      </table>
    </div>
    """
    send_html_email(email, user_subject, user_html)

    # Send notification email to support team
    team_subject = f"[Mira Bot] New Support Query from {name}"
    team_html = f"""
    <div style='font-family:Roboto,Arial,sans-serif;background:#f6f8fa;padding:0;margin:0;'>
      <table width='100%' bgcolor='#f6f8fa' cellpadding='0' cellspacing='0' style='padding:0;margin:0;'>
        <tr><td align='center'>
          <table width='100%' style='max-width:520px;background:#fff;border-radius:14px;box-shadow:0 2px 16px #0002;margin:32px 0 24px 0;padding:0 0 32px 0;'>
            <tr>
              <td style='background:#F72534;border-radius:14px 14px 0 0;padding:32px 0 18px 0;text-align:center;'>
                <img src='https://cdn-icons-png.flaticon.com/512/4712/4712035.png' alt='Mira Bot' width='56' height='56' style='border-radius:50%;background:#fff;padding:6px 6px 2px 6px;box-shadow:0 2px 8px #0001;'>
                <h1 style='color:#fff;font-size:2rem;margin:18px 0 0 0;font-weight:800;letter-spacing:1px;'>Medha Tech Support</h1>
              </td>
            </tr>
            <tr><td style='padding:32px 32px 0 32px;'>
              <h2 style='color:#F72534;font-size:1.3rem;margin-bottom:8px;'>New Support Query Received</h2>
              <div style='background:#f6f8fa;border-radius:8px;padding:18px 18px 12px 18px;margin:18px 0 24px 0;'>
                <h3 style='color:#F72534;font-size:1.08rem;margin:0 0 10px 0;'>Query Details</h3>
                <table style='width:100%;font-size:1.01rem;color:#222;'>
                  <tr><td style='padding:4px 0;'><b>Name:</b></td><td>{name}</td></tr>
                  <tr><td style='padding:4px 0;'><b>Email:</b></td><td>{email}</td></tr>
                  <tr><td style='padding:4px 0;'><b>Phone:</b></td><td>{phone}</td></tr>
                  <tr><td style='padding:4px 0;'><b>Category:</b></td><td>{category or 'N/A'}</td></tr>
                  <tr><td style='padding:4px 0;vertical-align:top;'><b>Description:</b></td><td>{description}</td></tr>
                </table>
              </div>
              <p style='color:#444;font-size:1.04rem;margin:0 0 18px 0;'>Please follow up with the user as soon as possible.</p>
            </td></tr>
            <tr><td style='padding:0 32px;'>
              <hr style='border:none;border-top:1.5px solid #f3f3f3;margin:24px 0;'>
              <p style='color:#888;font-size:0.98rem;text-align:center;'>This is an automated message from <b>Mira Bot</b> 🤖<br>Medha Tech Solutions Pvt. Ltd.<br><a href='https://medhatech.in' style='color:#F72534;text-decoration:none;'>medhatech.in</a></p>
            </td></tr>
          </table>
        </td></tr>
      </table>
    </div>
    """
    send_html_email(SUPPORT_EMAIL, team_subject, team_html)

    return jsonify({'success': True, 'message': 'Query submitted successfully.'})

@app.route('/query', methods=['GET'])
def get_queries():
    db = get_db()
    cur = db.execute('SELECT * FROM support_queries ORDER BY created_at DESC')
    queries = [dict(row) for row in cur.fetchall()]
    for q in queries:
        if q['file_path']:
            q['file_url'] = '/uploads/' + os.path.basename(q['file_path'])
    return jsonify(queries)

# Endpoint to update progress field
@app.route('/update_progress', methods=['POST'])
def update_progress():
    data = request.json
    query_id = data.get('id')
    new_progress = data.get('progress')
    allowed = ['Open', 'In Progress', 'Resolved', 'Closed']
    if not query_id or not new_progress or new_progress not in allowed:
        return jsonify({'success': False, 'message': 'Missing or invalid id/progress'}), 400
    db = get_db()
    db.execute('UPDATE support_queries SET progress = ? WHERE id = ?', (new_progress, query_id))
    db.commit()
    return jsonify({'success': True, 'message': 'Progress updated.'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Serve static files (for CSS/JS if needed)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
