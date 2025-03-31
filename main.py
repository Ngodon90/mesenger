from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Thiết lập API key của Gemini AI (Google Generative AI)
GENAI_API_KEY = "AIzaSyCeSZFV-F0lCXCVeImSimDN6qNafLI-erw"  # Thay bằng API key thực của bạn
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Token xác minh webhook với Facebook
VERIFY_TOKEN = "090216171119"

@app.route("/", methods=["GET"])
def home():
    return "Chatbot AI is running!", 200

# Webhook Facebook để nhận tin nhắn từ người dùng
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Xác thực Webhook với Facebook
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    elif request.method == 'POST':
        data = request.json
        handle_facebook_message(data)  # Gửi tin nhắn đến AI xử lý
        return jsonify({"status": "received"}), 200

def handle_facebook_message(data):
    """ Xử lý tin nhắn từ Facebook và gửi phản hồi """
    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging["sender"]["id"]
            if "message" in messaging:
                user_message = messaging["message"].get("text", "")
                bot_reply = generate_ai_response(user_message)
                send_message_to_facebook(sender_id, bot_reply)

def generate_ai_response(user_input):
    """ Gửi tin nhắn người dùng đến Gemini AI và nhận phản hồi """
    try:
        response = model.generate_content(user_input)
        return response.text.strip() if response.text else "Xin lỗi, tôi không hiểu câu hỏi của bạn."
    except Exception as e:
        print("Lỗi khi gọi Gemini AI:", str(e))
        return "Xin lỗi, tôi đang gặp sự cố kỹ thuật."

def send_message_to_facebook(recipient_id, message):
    """ Gửi phản hồi từ chatbot đến Facebook Messenger """
    PAGE_ACCESS_TOKEN = "EAAUTpVmrNMMBO9Um3qYZBLKlEUkK9cC3iTZBaB3qnlxvfzATmcVhsIbs1SooRtNuftMkZBw67QPgTAZCZA4MsHdUVr5EIDoiwZBj6j4iCEQm3WQGGqr8mDUZAHsHUeqVT4NVoCX2KewHQ2n6pruERs5i74lz8NCggMT5OmZCdC4ADfm3dCZCO7J2WP3q8kXaVmagG"  # Thay bằng token thực của bạn
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
