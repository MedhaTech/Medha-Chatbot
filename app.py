from flask import Flask, request, jsonify, send_from_directory, render_template_string
import requests
import os

app = Flask(__name__)

# Load data.txt as context
with open('data.txt', 'r', encoding='utf-8') as f:
    DATA_CONTEXT = f.read()

GEMINI_API_KEY = 'AIzaSyAiVocj1iTTpvUrT-EfR0vPQBdRFLQ5kC0'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GEMINI_API_KEY

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
You are Bubby, your friendly virtual assistant to help with this website. Answer the user's question based ONLY on the following context. If the answer is not in the context, politely say you don't know.

Context:
{DATA_CONTEXT}

User: {user_message}
Bubby:"""

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
    except Exception:
        bot_reply = "Sorry, I couldn't process your request."
    return jsonify({'reply': bot_reply})

# Serve static files (for CSS/JS if needed)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
    