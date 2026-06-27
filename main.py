import os
from flask import Flask, request, jsonify

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Initialize Groq client using your environment variables set on Render
from groq import Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Prompt message is required"}), 400

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful and advanced AI core companion named Aadhunik Manushya."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_response = completion.choices[0].message.content
        return jsonify({"response": bot_response}), 200

    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        return jsonify({"error": "Failed to communicate with Groq compute engine"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)