import requests

# Your bot token and chat ID
BOT_TOKEN = "7541875255:AAFsaW2dOmRA-VZxE-umbfvxcqRZMC-XUbQ"
CHAT_ID = "2117478694"

# Your test message
TEST_MESSAGE = "✅ SystemPulse Alert Test: This message was sent successfully via Telegram Bot!"

def send_telegram_message(token: str, chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print("✅ Message sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send message: {e}")

if __name__ == "__main__":
    send_telegram_message(BOT_TOKEN, CHAT_ID, TEST_MESSAGE)
