# 🌐 24/7 Cloud Mobile Access & Standby Sentinel for Aradhya

This subsystem allows Alpesh Sir to access **Aradhya** from any mobile phone, tablet, or web browser 24 hours a day, 7 days a week, **even when the physical laptop is completely powered off, asleep, or unplugged**.

---

## ⚡ How It Operates (When Laptop is Off)

1. **Dual-Node Architecture**:
   - **Local Laptop (Node A)**: Handles deep OS automation, process management, shell commands, and hardware controls when powered on.
   - **Cloud Standby Sentinel (Node B)**: Runs 24/7 on free cloud hosting (Render.com free tier, Google Cloud Run, Railway, or Hugging Face Spaces).
2. **Access Anywhere from Any Device**:
   - **Mobile Web Portal**: Open the cloud URL (e.g. `https://aradhya-cloud.onrender.com` or local `http://localhost:8080`) from any phone browser.
   - **Telegram Bot**: Send voice memos or text messages directly to your Telegram bot.
3. **Automatic Offline Task Queuing**:
   - If you ask general questions, seek advice, or brainstorm, Aradhya answers immediately using Gemini in the cloud.
   - If you command a laptop-specific directive (e.g., *"સ્પીડ બૂસ્ટ કરો"*, *"સિક્યુરિટી સ્કેન ચલાવો"*, *"ઓપન ફાઇલ"*), Aradhya recognizes your laptop is off and securely saves the directive into the **Cloud Task Mailbox**.
   - The moment your laptop turns on, local Aradhya automatically downloads the queued directives, executes them end-to-end, and reports the completion!

---

## 🚀 Free 1-Click Cloud Deployment (Render.com / Railway / Cloud Run)

You can deploy Node B in 2 minutes for free:
1. Create a free account on [Render.com](https://render.com).
2. Click **New +** -> **Web Service**.
3. Select this repository (or upload the `cloud_mobile_bridge` directory).
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn mobile_agent_server:app --host 0.0.0.0 --port $PORT`
6. Set Environment Variables:
   - `GEMINI_API_KEY` = `Your Gemini API Key`
   - `TELEGRAM_BOT_TOKEN` = `Your Telegram Bot Token (from @BotFather, optional)`
7. Click **Deploy Web Service**.
