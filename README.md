# 🤖 Mira: The Medha Tech AI Chatbot

**Mira** is a state-of-the-art, context-aware AI chatbot developed for Medha Tech. Powered by Google's Gemini 2.0 Flash API and built on a robust Flask backend, Mira delivers precise, context-driven responses exclusively from your curated knowledge base (`data.txt`). Mira is the ideal solution for organizations seeking a reliable, on-brand FAQ assistant for their digital platforms.

---

## Key Features

- **Context-Restricted Answers:** Mira responds strictly based on the information provided in `data.txt`, ensuring accuracy and eliminating hallucinations.
- **Modern Web Interface:** Seamless user experience via an intuitive web UI (`chat_ui.html`).
- **Powered by Gemini 2.0 Flash:** Leverages Google's advanced Generative Language API for fast, intelligent responses.
- **Customizable & Lightweight:** Easily adaptable to your brand's look and feel with static file support for CSS/JS.
- **Secure & Private:** No external data sources—Mira only references your supplied context.

---

## How Mira Works

1. Users interact with Mira through the `chat_ui.html` interface.
2. User queries are received by the Flask backend.
3. The backend constructs a prompt using the context from `data.txt`.
4. This prompt is sent to the Gemini API for processing.
5. Mira returns a contextually accurate response, displayed in the chat interface.

---

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Flask (`pip install flask`)
- Requests library (`pip install requests`)
- A valid Google Gemini API key

### Installation & Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/medha-mira-chatbot.git
cd medha-mira-chatbot

# Install dependencies
pip install flask requests

# Add your Gemini API key to the environment or configuration as required

# Start the application
python app.py
```

---

## Customization

- **Knowledge Base:** Update `data.txt` with your organization's FAQs or reference material.
- **UI/UX:** Modify `chat_ui.html` and associated static files to match your branding.

---

## Deployment

Mira can be deployed on any standard Python/Flask-compatible server. For production environments, consider using a WSGI server such as Gunicorn and a reverse proxy (e.g., Nginx) for optimal performance and security.

---

## License & Support

For licensing, support, or custom integration inquiries, please contact the Medha Tech team.

---

**Mira – Your Trusted AI Assistant for Medha Tech**

## API Endpoints

### /update_progress

Update the progress status of a support query.

- **Method:** POST
- **URL:** `/update_progress`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "id": 1,
    "progress": "Resolved"
  }
  ```
  - `id`: The ID of the support query to update.
  - `progress`: The new status. Allowed values: `"Open"`, `"In Progress"`, `"Resolved"`, `"Closed"`.

- **Response:**
  - Success:
    ```json
    { "success": true, "message": "Progress updated." }
    ```
  - Failure (e.g., missing or invalid data):
    ```json
    { "success": false, "message": "Missing or invalid id/progress" }
    ```

## Environment Variables (.env)

Create a `.env` file in the project root with the following variables:

```
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SUPPORT_EMAIL=support@medhatech.in
MIRA_EMAIL=mira@medhatech.in
GEMINI_API_KEY=your_gemini_api_key
```

- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: Used for sending support emails from the chatbot.
- `SUPPORT_EMAIL`: The email address shown as the support contact (default is `support@medhatech.in` if not set).
- `MIRA_EMAIL`: The email address used by Mira for outgoing messages (default is `mira@medhatech.in` if not set).
- `GEMINI_API_KEY`: Your Google Gemini API key (required).

**Note:** All variables are loaded automatically from the `.env` file at startup. Never commit your `.env` file to version control.




