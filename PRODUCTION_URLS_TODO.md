# Production URL Replacement Checklist for Medha Tech Flask App

This file lists all locations in the codebase where URLs are hardcoded or need to be updated for production deployment. Update these before going live!

---

## 1. `app.py`

- **Line ~89**: Hardcoded PHP API URL for bot data:
  ```python
  bot_api_url = f'http://localhost/Mira/api/get_bot_data.php?bot_id={bot_id}'
  ```
  **Replace `http://localhost/Mira/` with your production PHP API base URL.**

- **Email templates**: Links to `https://medhatech.in` are used in email HTML. If your production domain is different, update these in the email HTML in `submit_query()`.

---

## 2. `chat_ui.html`

- **Line ~684**: JavaScript fetches bot data from PHP API:
  ```js
  const apiBase = 'http://localhost/Mira/';
  // ...
  const res = await fetch(apiBase + 'api/get_bot_data.php?bot_id=' + bot_id);
  ```
  **Replace `http://localhost/Mira/` with your production PHP API base URL.**

- **Line ~864**: Support form submission URL:
  ```js
  const res = await fetch('http://localhost/Mira/submit_query.php', {
      method: 'POST',
      body: formData
  });
  ```
  **Replace `http://localhost/Mira/submit_query.php` with your production endpoint.**

---

## 3. `test.html`

- **Line ~41**: Widget iframe source URL:
  ```js
  iframe.src = 'http://127.0.0.1:5001'; // CHANGE THIS to your deployed URL!
  ```
  **Replace with your production Flask app URL.**

---

## 4. Environment Variables

- Ensure all API keys, SMTP settings, and email addresses in your `.env` file are set for production.

---

**Tip:**
- Consider moving all URLs to environment variables or a config file for easier management.
- Double-check CORS settings for production security. 