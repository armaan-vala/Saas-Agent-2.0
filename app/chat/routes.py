import os
from flask import request, jsonify
from groq import Groq
from app.chat import chat_bp

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or not 'message' in data or not 'system_prompt' in data:
        return jsonify({'error': 'Missing message or system_prompt'}), 400

    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": data['system_prompt']
                },
                {
                    "role": "user",
                    "content": data['message']
                }
            ],
            model="gemma2-9b-it",
        )
        response_content = chat_completion.choices[0].message.content
        return jsonify({'response': response_content})

    except Exception as e:
        return jsonify({'error': str(e)}), 500