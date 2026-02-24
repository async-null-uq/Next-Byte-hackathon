import time, json, smtplib, threading, os
from datetime import datetime
from imap_tools import MailBox
from email.message import EmailMessage
from openai import OpenAI
import telebot

# --- CONFIG ---
EMAIL = ""
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
    data = []
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: data = json.load(f)
        except: data = []
    data.append(email_data)
    with open(MEMORY_FILE, "w") as f: json.dump(data, f, indent=4)

def get_history(sender_email):
    if not os.path.exists(MEMORY_FILE): return "No previous history."
    try:
        with open(MEMORY_FILE, "r") as f: data = json.load(f)
        relevant = [m for m in data if sender_email.lower() in str(m.get('from', '')).lower()]
        context = "\n".join([f"Date: {m['date']} | Body: {m['body'][:150]}" for m in relevant[-3:]])
        return context if context else "No past history found."
    except: return "History error."

def check_importance(subject, body):
    prompt = f"Subject: {subject}\nBody: {body}\n\nIs this 'Important' or 'Junk'? Reply 1 word only: Important or Junk."
    try:
        res = client.chat.completions.create(
            model="arcee-ai/trinity-large-preview:free",
            messages=[{"role": "user", "content": prompt}]
        )
        return "important" in res.choices[0].message.content.lower()
    except: return True

# --- TELEGRAM HANDLERS ---

@bot.message_handler(func=lambda m: m.text.lower() == 'send')
def handle_send(message):
    if pending_reply["to"]:
        bot.send_message(CHAT_ID, " *Sending Email...*")
        try:
            msg = EmailMessage()
            msg.set_content(pending_reply["body"])
            msg['Subject'] = f"Re: {pending_reply['subject']}"
            msg['From'] = EMAIL
            msg['To'] = pending_reply["to"]

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL, PASSWORD)
                smtp.send_message(msg)

            save_to_memory({
                "id": f"sent_{int(time.time())}",
                "date": str(datetime.now()),
                "from": f"Anay Yadav (to {pending_reply['to']})",
                "subject": f"Re: {pending_reply['subject']}",
                "body": pending_reply["body"]
            })
            bot.send_message(CHAT_ID, " *Sent! Saved to Anay's memory bank.*")
            pending_reply.update({"to": "", "subject": "", "body": ""})
        except Exception as e:
            bot.send_message(CHAT_ID, f" *Error:* {e}")

@bot.message_handler(func=lambda m: m.text.lower().startswith('alter '))
def handle_alter(message):
    feedback = message.text[6:]
    bot.send_message(CHAT_ID, " *Updating draft...*")
    
    prompt = (
        f"Original Email: {pending_reply['orig_msg']}\nUser Notes: {feedback}\n\n"
        f"You are Anay Yadav. Rewrite the professional response based on the notes. "
        f"Output ONLY the email text. No explanations. Sign as Anay Yadav."
    )
    new_draft = client.chat.completions.create(
        model="arcee-ai/trinity-large-preview:free",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content
    
    pending_reply["body"] = new_draft
    bot.send_message(CHAT_ID, f" *REVISED DRAFT:* \n`{new_draft}`\n\n'send' | 'alter [notes]'")

# --- CORE MONITOR ---

def monitor_inbox():
    print("InboxSentinel is Active. Monitoring for Anay Yadav...")
    while True:
        try:
            with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD) as mb:
                for msg in mb.fetch(limit=1, reverse=True):
                    if msg.uid in seen_uids: continue
                    seen_uids.add(msg.uid)

                    if not check_importance(msg.subject, msg.text):
                        continue

                    history = get_history(msg.from_)
                    
                    # STRICT PROMPT FOR NO EXPLANATIONS
                    prompt = (
                        f"SYSTEM: You are Anay Yadav's AI assistant. Output ONLY the response text. Do not explain your reasoning.\n\n"
                        f"HISTORY:\n{history}\n\n"
                        f"NEW MAIL FROM {msg.from_}:\n{msg.text}\n\n"
                        f"Draft a concise response. Sign off as 'Anay Yadav'."
                    )
                    
                    ai_draft = client.chat.completions.create(
                        model="arcee-ai/trinity-large-preview:free",
                        messages=[{"role": "user", "content": prompt}]
                    ).choices[0].message.content

                    pending_reply.update({
                        "to": msg.from_, 
                        "subject": msg.subject, 
                        "body": ai_draft, 
                        "orig_msg": msg.text
                    })

                    bot.send_message(CHAT_ID, 
                        f" *NEW PRIORITY MAIL*\n"
                        f" *From:* {msg.from_}\n"
                        f" *Subject:* {msg.subject}\n\n"
                        f" *MESSAGE:* \n_{msg.text[:600]}..._\n\n"
                        f" *AI SUGGESTED REPLY:* \n`{ai_draft}`\n\n"
                        f"--- \n'send' | 'alter [notes]' | 'ignore'",
                        parse_mode="Markdown"
                    )
        except Exception as e: 
            print(f"Connection Error: {e}")
        time.sleep(20)

if __name__ == "__main__":
    threading.Thread(target=monitor_inbox, daemon=True).start()
    bot.infinity_polling()
