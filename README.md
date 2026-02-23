# 🛡️ InboxSentinel AI
### *The Memory-Augmented Executive Assistant for Your Inbox*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AI-Powered](https://img.shields.io/badge/AI-Arcee--Trinity--Large-orange.svg)](https://openrouter.ai/arcee-ai/trinity-large-preview:free/)
[![Interface](https://img.shields.io/badge/UI-Telegram-0088cc.svg)](https://telegram.org/)

**InboxSentinel** is a state-of-the-art AI Agent designed for high-stakes productivity. It doesn't just "filter" emails—it remembers your professional history, triages incoming messages by importance, and lets you respond to critical business leads from Telegram with a single click.

**Why we use JSON?"**: We chose a JSON-based persistent memory to keep the agent lightweight and privacy-focused, ensuring all user data stays local and easily auditable without third-party cloud database overhead.

---

## 🚀 The Problem
In 2026, we are drowning in "Smart" newsletters and junk. Critical emails from clients or partners often get lost in the noise. Managing these on a mobile device is clunky, and standard "Auto-Reply" bots sound like robots.

## ✨ The Solution: Human-in-the-Loop Intelligence
InboxSentinel bridges the gap between **Automation** and **Authenticity**:

* **🎯 Priority Triage:** Uses LLM intent analysis to ignore junk and only notify you of high-value interactions.
* **🧠 Deep Memory (RAG):** It scans your `clean_memory.json` (past interactions) to ensure drafts match your specific tone and previous context.
* **📱 Zero-Friction UI:** Receive a notification on Telegram while on the move, review the AI draft, and click **"Send"**—all without opening a laptop.
* **✍️ Dynamic Refinement:** Not happy with a draft? Use the `alter` or `edit` commands to tweak the AI's response in real-time.

---

## 🛠️ Tech Stack
* **Model:** `arcee-ai/trinity-large-preview` (via OpenRouter) for high-reasoning drafting.
* **Backend:** Python 3.x
* **Communication:** IMAP (Gmail) for ingestion, SMTP for secure transmission.
* **Interface:** Telebot (Telegram API) for the mobile "Command Center."
* **Database:** JSON-based persistent memory (Cleaned & Pre-processed).

---

## ⚙️ How It Works
1.  **Ingest:** Monitor Gmail via IMAP for new unread messages.
2.  **Filter:** AI classifies the email as `Important` or `Junk`.
3.  **Recall:** If important, the agent pulls the last 5-10 interactions with that sender.
4.  **Draft:** AI generates a concise, professional reply using that history.
5.  **Human Approval:** You receive a Telegram alert with buttons to **Send**, **Alter**, or **Ignore**.
6.  **Update:** Once sent, the conversation is saved back to `clean_memory.json` to improve future drafts.

---

## 🛠️ Installation & Environment Setup

To get **InboxSentinel AI** running on your local machine, follow these steps. 

### 1. Prerequisites
Ensure you have **Python 3.9+** installed. You will also need a **Telegram Bot Token** (from [BotFather](https://t.me/botfather)) and a **Google App Password** if you are using Gmail.

### 2. Install Required Libraries
Run the following command to install all necessary dependencies for the AI engine, mail handling, and Telegram interface:

```bash
pip install imap-tools pyTelegramBotAPI openai beautifulsoup4 python-dotenv
```
---

## 🔐 Gmail Security & App Passwords

Since **InboxSentinel AI** interacts directly with your inbox, you must use a **Google App Password**. Standard passwords will not work due to Google's security protocols.

### Step 1: Enable 2-Step Verification (Required)
Google only allows App Passwords if your account is secured with 2FA.
1. Go to your [Google Account Settings](https://myaccount.google.com/).
2. On the left navigation panel, select **Security**.
3. Under *"How you sign in to Google,"* ensure **2-Step Verification** is turned **ON**.
4. Follow the on-screen prompts to link your phone or backup codes.

### Step 2: Generate an App Password
1. Once 2-Step Verification is active, go to the [App Passwords Page](https://myaccount.google.com/apppasswords).
2. **App Name:** Enter `InboxSentinel` (or any name you prefer).
3. Click **Create**.
4. **Copy the 16-character code** in the yellow bar.
   > **⚠️ Important:** This is the only time you will see this code. Paste it directly into your `.env` file under the `PASSWORD` field. 

### Step 3: IMAP Settings
Ensure your Gmail is ready to talk to the AI Agent:
1. Open **Gmail** in your browser and go to **Settings** (gear icon) > **See all settings**.
2. Click the **Forwarding and POP/IMAP** tab.
3. In the "IMAP access" section, select **Enable IMAP**.
4. Click **Save Changes** at the bottom.

---

## ☁️ Running on Google Colab

While **InboxSentinel AI** can be hosted on any cloud provider (AWS, Heroku, Railway), we have optimized this version for **Google Colab** to leverage high-speed processing and easy storage integration via Google Drive.

### 1. Mount Google Drive
To ensure your `clean_memory.json` persists even after your Colab session ends, run the following snippet in your notebook:

```python
from google.colab import drive
drive.mount('/content/drive')

# Change directory to your project folder
import os
os.chdir('/content/drive/My Drive/Next-Byte/')
```

---

## 🧠 Memory Ingestion: Powering the AI Brain

For **InboxSentinel AI** to provide contextually accurate responses, it needs to understand your communication style and past interactions. This is achieved through an initial data extraction phase.

### Why Extract Your Emails?
Unlike standard bots, InboxSentinel uses a **Local Memory Engine**. By extracting your past emails:
* **Relationship Context:** The AI knows if a sender is a long-term client or a new contact.
* **Tone Matching:** The agent learns how you typically greet, sign off, and structure your professional replies.
* **Contextual RAG:** When a new mail arrives, the system retrieves relevant historical snippets to ensure the draft is grounded in fact, not hallucinations.

### 📥 How to Extract
Before running the main agent, you need to populate your local `clean_memory.json`. 

1. Navigate to the `Extract-mail.py` file in this repository.
2. Ensure your `.env` credentials are set.
3. Run the extraction script: Extract-mail.py in my repo
4. Run the Cleaning scrip to clean your Extracted json from: clean-json.py in my repo

---

## 🤖 Powering the Intelligence: OpenRouter AI

**InboxSentinel AI** is model-agnostic, but it is optimized for high-reasoning tasks. We use **OpenRouter** as our gateway to access the world’s most powerful Large Language Models (LLMs).

### 1. Create an Account
1. Visit [OpenRouter.ai](https://openrouter.ai/).
2. Sign up using your Google account or email.
3. Go to **any model you like** in the dashboard and click **"Quickstart"** where you get **"Create API key"**.
4. Copy your key and paste it into your `.env` file under `OPENROUTER_API_KEY`.

### 2. Choosing a Model
While you can use any model available on OpenRouter (GPT-4, Claude 3, etc.), we recommend and use:
* **Model:** `arcee-ai/trinity-large-preview:free`
* **Why?** It offers exceptional **Reasoning Capabilities**, allowing the agent to understand complex email threads and nuances. 
* **Cost:** This specific model is currently **free** to use, making this project highly accessible and cost-effective.

---
## 📱 Telegram Command Center Setup

To receive notifications and control the AI agent from your phone, you need to create your own Telegram Bot.

### 1. Create Your Bot
1. Open Telegram and search for [@BotFather](https://t.me/botfather).
2. Send the command `/newbot`.
3. Give your bot a **Name** (e.g., `MySentinel`) and a **Username** (ending in `_bot`).
4. **Copy the API Token** provided and paste it into your `.env` file under `TELEGRAM_TOKEN`.

### 2. Get Your Chat ID
The bot needs to know *who* to send the emails to.
1. Start a chat with your new bot and send any message (e.g., "Hello").
2. Search for [@userinfobot](https://t.me/userinfobot) in Telegram.
3. Send a message to it, and it will reply with your **ID** (a string of numbers).
4. Paste this ID into your `.env` file under `CHAT_ID`.

---

## 🚀 Deployment & Hosting

Once you have configured the `.env` file, you are ready to launch **InboxSentinel**.

### Running the Main Code
The "brain" of this project is located in `main-code.py`. This script handles the real-time monitoring of your inbox, AI reasoning, and Telegram interaction.

### 🏠 Where to Host?
* **For Permanent Use:** Since the agent needs to run 24/7 to monitor your mail, we recommend a VPS or a paid hosting plan (like Railway, Heroku, or a Raspberry Pi).
* **For Testing (Free):** If you are just testing or presenting, **Google Colab** works perfectly. 
    * Upload the repo files to your Google Drive.
    * Run the script in a Colab cell using `!python main.py`.
    * *Note: Ensure your Colab session doesn't time out during the monitoring phase.*

---

## ✅ All Set!
You are now ready to go. Run the script, sit back, and let **InboxSentinel AI** turn your cluttered inbox into a high-performance executive feed.
