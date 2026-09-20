import requests

# 1. Your Bot Token from @BotFather
TELEGRAM_BOT_TOKEN = "8963124698:AAF9RyAi9cM8GsWx4wboWupGg8blPMzN5X0"

# 2. Recipient Chat IDs (List of target Telegram IDs)
EMERGENCY_CHAT_IDS = [
    "8489128563",
    "7522780948",
    "1853265870"  # Replace with actual recipient Telegram User/Group ID
]

def send_emergency_telegram(name="Victim", sender_phone="Not Provided"):
    tracking_link = "https://manila-reprise-caboose.ngrok-free.dev/dashboard"
    
    # HTML formatted message body
    message_text = (
        f"🚨 <b>SHESHIELD EMERGENCY ALERT</b> 🚨\n\n"
        f"<b>Victim Name:</b> {name}\n"
        f"<b>Phone Number:</b> {sender_phone}\n\n"
        f"⚠️ <i>Needs urgent help! Track live location here:</i>\n"
        f"<a href='{tracking_link}'>{tracking_link}</a>"
    )

    url = f"https://api.telegram.org/bot{8489128563}/sendMessage"
    success = True

    for chat_id in EMERGENCY_CHAT_IDS:
        payload = {
            "chat_id": chat_id,
            "text": message_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            response = requests.post(url, json=payload, timeout=5)
            res_data = response.json()
            
            if response.status_code == 200 and res_data.get("ok"):
                print(f"✅ Telegram alert delivered to Chat ID: {chat_id}")
            else:
                print(f"❌ Telegram Error for {chat_id}: {res_data.get('description')}")
                success = False
        except Exception as e:
            print(f"❌ Exception sending Telegram alert: {e}")
            success = False

    return success