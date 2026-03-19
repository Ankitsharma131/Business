import os
import pandas as pd
import requests
import urllib.parse
import time
from datetime import datetime
import pytz

# --- FETCH SECRETS FROM GITHUB ---
SHEET_CSV_URL = os.getenv("SHEET_CSV_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def generate_wa_link(phone, name, amount):
    # Clean phone number (removes decimals/spaces)
    phone = str(phone).split('.')[0].strip().replace("+", "")
    if not phone.startswith("91"):
        phone = "91" + phone
        
    message = f"Hi {name}, you have a pre-approved loan of ₹{amount}. Reply YES to process this."
    encoded_msg = urllib.parse.quote(message)
    return f"https://wa.me/{phone}?text={encoded_msg}"

def main():
    # Set time to IST
    ist = pytz.timezone('Asia/Kolkata')
    today_str = datetime.now(ist).strftime('%Y-%m-%d')
    print(f"Checking leads for: {today_str}")

    # Read data
    df = pd.read_csv(SHEET_CSV_URL)
    
    # Filter for today's Date (Ensure column 'Date' exists in Sheet)
    df['Date'] = df['Date'].astype(str).str.strip()
    today_leads = df[df['Date'] == today_str]

    if today_leads.empty:
        print("No leads for today.")
        return

    for _, row in today_leads.iterrows():
        wa_link = generate_wa_link(row['Phone'], row['Name'], row['Amount'])
        
        msg = (
            f"<b>🚀 NEW LEAD: {row['Name']}</b>\n"
            f"Loan Amount: ₹{row['Amount']}\n"
            f"Phone: {row['Phone']}\n\n"
            f"👉 <a href='{wa_link}'>Open WhatsApp Chat</a>"
        )
        
        send_to_telegram(msg)
        time.sleep(1) # Prevent Telegram spam block

if __name__ == "__main__":
    main()
