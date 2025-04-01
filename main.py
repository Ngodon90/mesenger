from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import requests

app = Flask(__name__)

# Thiết lập API key của Gemini AI (Google Generative AI)
GENAI_API_KEY = "AIzaSyCeSZFV-F0lCXCVeImSimDN6qNafLI-erw"  # Thay bằng API key thực của bạn
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Token xác minh webhook với Facebook
VERIFY_TOKEN = "090216171119"
ACCESS_TOKEN = "EAAUTpVmrNMMBO9Um3qYZBLKlEUkK9cC3iTZBaB3qnlxvfzATmcVhsIbs1SooRtNuftMkZBw67QPgTAZCZA4MsHdUVr5EIDoiwZBj6j4iCEQm3WQGGqr8mDUZAHsHUeqVT4NVoCX2KewHQ2n6pruERs5i74lz8NCggMT5OmZCdC4ADfm3dCZCO7J2WP3q8kXaVmagG"  # Thay bằng token của bạn
#29082403008071049


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                message_text = messaging_event.get("message", {}).get("text")
                
                if message_text:
                    response_text = get_ai_response(message_text)
                    send_message(sender_id, response_text)

    return "EVENT_RECEIVED", 200


def get_ai_response(user_message):
    """ Gọi API Gemini AI để lấy câu trả lời """
    try:
        response = model.generate_content(user_message)
        return response.text.strip() if response.text else "Xin lỗi, tôi chưa hiểu."
    except Exception as e:
        print("Lỗi Google AI:", str(e))
        return "Xin lỗi, tôi đang gặp lỗi!"


def send_message(recipient_id, message_text):
    """ Gửi tin nhắn từ chatbot đến người dùng """
    payload = {
        "recipient": {"29082403008071049": recipient_id},
        "message": {"text": message_text}
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}",
        json=payload,
        headers=headers
    )

    print("Gửi tin nhắn:", response.json())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
