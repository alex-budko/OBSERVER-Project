from flask import Flask, request
import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = "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"

MODEL = "gpt-3.5-turbo"

@app.route('/api/generate-response', methods=['POST'])
def handle_response_generation():
    message = request.json['message']
    category = request.json['category']
    reply, _ = generate_response(samples, message, category)
    return {"response": reply}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
