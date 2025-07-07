# 🤖 ChatBot for Medha Tech — Bubby

**Bubby** is a lightweight Flask-based chatbot powered by Google’s Gemini 2.0 Flash API. It is designed to assist users by answering questions based strictly on your provided context file (`data.txt`). This makes it ideal for FAQ bots on product or service websites.

---

## ✨ Features

- 🔒 Answers only from the provided `data.txt` context (no hallucinations).
- 💬 Simple web UI (`chat_ui.html`) for user interaction.
- ⚡ Powered by Gemini 2.0 Flash (via Google Generative Language API).
- 📂 Static file support for custom CSS/JS styling.

---

## 🚀 How It Works

1. The chatbot interface loads from `chat_ui.html`.
2. User types a question.
3. The Flask backend formats a prompt with context from `data.txt`.
4. This prompt is sent to the Gemini API.
5. The API returns a response, which is then shown to the user as a reply from "Bubby".


---

## 🛠️ How to Run

### 🔧 Prerequisites

- Python 3.7+
- Flask (`pip install flask`)
- `requests` library (`pip install requests`)
- A valid Google Gemini API key

### ▶️ Start the App

```bash
# Clone the repo
git clone https://github.com/<your-username>/medha-chatbot.git
cd medha-chatbot

# Install dependencies
pip install flask requests

# Run the app
python app.py


