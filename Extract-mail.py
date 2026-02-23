import json
import os
from imap_tools import MailBox

# CONFIGURATION
EMAIL = ""
PASSWORD = ""  # Use a Google App Password, not your main password!
IMAP_SERVER = "imap.gmail.com"
JSON_FILE = "memory.json"

def extract_all_emails():
    # Load existing progress if it exists
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            all_emails = json.load(f)
        print(f"Loaded {len(all_emails)} existing emails from checkpoint.")
    else:
        all_emails = []

    print(f"Connecting to {IMAP_SERVER}...")

    try:
        with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD) as mailbox:
            # We fetch ALL emails, reverse=True gets the newest first
            # bulk=True makes it faster for large volumes
            print("Fetching email list... this might take a moment for 500+ mails.")

            count = 0
            for msg in mailbox.fetch(reverse=True):
                # Check if we already have this email (prevent duplicates)
                if any(e['id'] == msg.uid for e in all_emails):
                    continue

                email_data = {
                    "id": msg.uid,
                    "date": str(msg.date),
                    "from": msg.from_,
                    "subject": msg.subject,
                    "body": msg.text.strip()[:1500]  # Increased limit for better AI context
                }

                all_emails.append(email_data)
                count += 1

                # CHECKPOINT: Save every 10 emails
                if count % 10 == 0:
                    with open(JSON_FILE, "w", encoding="utf-8") as f:
                        json.dump(all_emails, f, indent=4)
                    print(f"Checkpoint: {len(all_emails)} total emails saved...")

            # Final save
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(all_emails, f, indent=4)

            print(f"DONE! Total emails in memory: {len(all_emails)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_all_emails()
