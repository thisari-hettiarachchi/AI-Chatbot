from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Replace with your own Gemini API Key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# Global chat history
chat_history = []

def ask_gemini(message):
    """
    Sends the full chat history to Gemini, appending the latest user message.
    """
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    # Add user message to chat history
    chat_history.append({
        "role": "user",
        "parts": [{"text": message}]
    })

    payload = {
        "contents": chat_history
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            bot_reply = result["candidates"][0]["content"]["parts"][0]["text"]
            chat_history.append({
                "role": "model",
                "parts": [{"text": bot_reply}]
            })
            return bot_reply
        else:
            return "Error: Could not get a valid response from Gemini AI."
    except Exception as e:
        return f"Error: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    bot_reply = None
    if request.method == "POST":
        user_message = request.form["user_input"]
        bot_reply = ask_gemini(user_message)
    return render_template("index.html", bot_reply=bot_reply)

if __name__ == "__main__":
    app.run(debug=True)
