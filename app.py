from flask import Flask, request, jsonify, send_from_directory, render_template_string, g
from werkzeug.utils import secure_filename
import requests
import os
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load data.txt as context
with open('data.txt', 'r', encoding='utf-8') as f:
    DATA_CONTEXT = f.read()

GEMINI_API_KEY = 'AIzaSyAzGRJ-6AeIMAl_ugfKq5ML2cp7065_e_Y'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GEMINI_API_KEY

DATABASE = 'support_queries.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'txt', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
