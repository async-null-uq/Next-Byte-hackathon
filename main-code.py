import time, json, smtplib, threading, os
from datetime import datetime
from imap_tools import MailBox
from email.message import EmailMessage
from openai import OpenAI
import telebot

# --- CONFIG ---
EMAIL = "@gmail.com"
PASSWORD = ""
IMAP_SERVER = "imap.gmail.com"
OPENROUTER_API_KEY = ""
TELEGRAM_TOKEN = ""
CHAT_ID = ""
MEMORY_FILE = "clean_memory.json"

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

pending_reply = {"to": "", "subject": "", "body": "", "orig_msg": ""}
seen_uids = set()

# --- HELPER FUNCTIONS ---

def save_to_memory(email_data):
    """Saves new interactions to the JSON database."""
    data = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f: data = json.load(f)
    data.append(email_data)
    with open(MEMORY_FILE, "w") as f: json.dump(data, f, indent=4)

def get_history(sender_email):
    """Retrieves last 5 interactions with this sender."""
    if not os.path.exists(MEMORY_FILE): return "No previous history."
    with open(MEMORY_FILE, "r") as f: data = json.load(f)
    relevant = [m for m in data if sender_email.lower() in m.get('from', '').lower()]
    context = "\n".join([f"Date: {m['date']} | Sub: {m['subject']} | Body: {m['body'][:200]}" for m in relevant[-5:]])
    return context if context else "No specific past conversation found."

def check_importance(subject, body):
    """AI determines if the mail needs immediate attention."""
    # Change your prompt to:
    prompt = f"Analyze this email:\nSubject: {subject}\nBody: {body}\n\nThink step-by-step: Who is the sender? Is there a call to action? Then, conclude with 'Classification: Important' or 'Classification: Junk'."
    res = client.chat.completions.create(
        model="arcee-ai/trinity-large-preview:free",
        messages=[{"role": "user", "content": prompt}]
    )
    return "important" in res.choices[0].message.content.lower()

# --- TELEGRAM HANDLERS ---

@bot.message_handler(func=lambda m: m.text.lower() == 'send')
def handle_send(message):
    if pending_reply["to"]:
        bot.reply_to(message, "*Sending...*")
        msg = EmailMessage()
        msg.set_content(pending_reply["body"])
        msg['Subject'] = f"Re: {pending_reply['subject']}"
        msg['From'] = EMAIL
        msg['To'] = pending_reply["to"]

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL, PASSWORD)
            smtp.send_message(msg)

        # SAVE TO MEMORY
        save_to_memory({
            "id": "sent_" + str(time.time()),
            "date": str(datetime.now()),
            "from": f"ME (to {pending_reply['to']})",
            "subject": f"Re: {pending_reply['subject']}",
            "body": pending_reply["body"]
        })

        bot.send_message(CHAT_ID, "*Sent & Saved to Memory!*")
        pending_reply.update({"to": "", "subject": "", "body": ""})

# --- CORE MONITOR ---

def monitor_inbox():
    while True:
        try:
            with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD) as mb:
                for msg in mb.fetch(limit=1, reverse=True):
                    if msg.uid in seen_uids: continue
                    seen_uids.add(msg.uid)

                    # 1. Check Importance
                    if not check_importance(msg.subject, msg.text):
                        print(f"Skipping Junk: {msg.subject}")
                        continue

                    # 2. Get Past History
                    history = get_history(msg.from_)

                    # 3. Craft Response based on Memory
                    prompt = f"HISTORY:\n{history}\n\nNEW MAIL FROM {msg.from_}:\n{msg.text}\n\nDraft a concise, professional 1-2 sentence response based on our history."
                    ai_draft = client.chat.completions.create(
                        model="arcee-ai/trinity-large-preview:free",
                        messages=[{"role": "user", "content": prompt}]
                    ).choices[0].message.content

                    pending_reply.update({"to": msg.from_, "subject": msg.subject, "body": ai_draft})

                    # 4. Save incoming to memory
                    save_to_memory({"id": msg.uid, "date": str(msg.date), "from": msg.from_, "subject": msg.subject, "body": msg.text})

                    bot.send_message(CHAT_ID,
                        f"*PRIORITY MAIL*\n*From:* {msg.from_}\n\n"
                        f"*PAST CONTEXT:* _{history[:150]}..._\n\n"
                        f"*MEMORY-BASED DRAFT:* \n`{ai_draft}`\n\n"
                        f"--- \n'send' | 'alter [notes]' | 'ignore'"
                    )
        except Exception as e: print(f"Error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    print("Smart Agent with Memory is Live.")
    threading.Thread(target=monitor_inbox, daemon=True).start()
    bot.infinity_polling()
