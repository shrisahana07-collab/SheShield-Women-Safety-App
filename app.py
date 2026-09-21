import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static', template_folder='templates')

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Emergency Contact Telegram Chat IDs
EMERGENCY_CHAT_IDS = [
    "7522780948",
    "8644000785",
    "8489128563",
    "1853265870",
    "7989230916"
]

# PythonAnywhere Free Tier Proxy Configuration
PROXIES = {
    'http': 'http://proxy.server:3128',
    'https': 'http://proxy.server:3128'
}

# Directory for storing ESP32-CAM photos
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'captures')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Shared memory state for hardware sync & dashboard live updates
victim_location = {"lat": None, "lng": None}
latest_capture_filename = None
sos_active_state = False


def send_telegram_photo(filepath):
    """Utility to forward captured attacker photo to all emergency contacts via PA Proxy"""
    if not TELEGRAM_BOT_TOKEN or not os.path.exists(filepath):
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    for chat_id in EMERGENCY_CHAT_IDS:
        try:
            with open(filepath, 'rb') as photo:
                payload = {"chat_id": chat_id, "caption": "🚨 ATTACKER SNAPSHOT CAPTURED!"}
                files = {"photo": photo}
                requests.post(url, data=payload, files=files, proxies=PROXIES, timeout=10)
        except Exception as e:
            print(f"Error sending photo to {chat_id}: {e}")


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/instructions')
def instructions():
    return render_template('instructions.html')


@app.route('/update-location', methods=['POST'])
def update_location():
    global victim_location
    data = request.get_json(silent=True) or request.form
    if data and 'lat' in data and 'lng' in data:
        victim_location['lat'] = float(data['lat'])
        victim_location['lng'] = float(data['lng'])
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400


@app.route('/get-location', methods=['GET'])
def get_location():
    return jsonify(victim_location)


@app.route('/trigger_sos', methods=['POST'])
def trigger_sos():
    global sos_active_state
    sos_active_state = True
    
    data = request.get_json(silent=True) or {}
    victim_name = data.get('name', 'Victim')
    victim_phone = data.get('phone', 'Not Provided')

    tracking_link = "https://shrisahana.pythonanywhere.com/dashboard"
    message = f"🚨 SHESHIELD EMERGENCY SOS! 🚨\n\nUser: {victim_name}\nPhone: {victim_phone}\n\nLive Location Tracking:\n{tracking_link}"

    sent_count = 0
    if TELEGRAM_BOT_TOKEN:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        for chat_id in EMERGENCY_CHAT_IDS:
            payload = {
                "chat_id": chat_id,
                "text": message
            }
            try:
                response = requests.post(url, json=payload, proxies=PROXIES, timeout=10)
                if response.status_code == 200:
                    sent_count += 1
                else:
                    print(f"Telegram error ({chat_id}): {response.text}")
            except Exception as e:
                print(f"Error sending to {chat_id}: {e}")

    return jsonify({
        "status": "success",
        "telegram_sent_to": sent_count
    }), 200


@app.route('/upload_camera_frame', methods=['POST'])
def upload_camera_frame():
    global latest_capture_filename
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    filename = "latest_attacker.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    latest_capture_filename = filename

    # Forward photo to Telegram chat IDs using PythonAnywhere Proxy
    send_telegram_photo(filepath)

    return jsonify({
        "status": "success",
        "image_url": f"/static/captures/{filename}"
    }), 200


@app.route('/get_latest_status', methods=['GET'])
def get_latest_status():
    image_url = f"/static/captures/{latest_capture_filename}" if latest_capture_filename else None
    return jsonify({
        "sos_active": sos_active_state,
        "image_url": image_url,
        "location": victim_location
    }), 200


@app.route('/reset_sos', methods=['POST'])
def reset_sos():
    global sos_active_state
    sos_active_state = False
    return jsonify({"status": "success", "message": "SOS state reset"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)