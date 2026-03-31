import os
import base64
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables robustly
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
# Enable CORS so your React frontend can call this api/index.py function
CORS(app)

# Initialize Clients
groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

cerebras_client = Cerebras(
    api_key=os.getenv("CEREBRAS_API_KEY")
)

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file']
        image_base64 = base64.b64encode(file.read()).decode('utf-8')

        # STAGE 1: OCR with Groq Llama 4 Scout
        ocr_response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all food items and their prices exactly as shown."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }]
        )
        extracted_text = ocr_response.choices[0].message.content

        # STAGE 2: Reasoning with Cerebras Llama 3.1 8B
        analysis_response = cerebras_client.chat.completions.create(
            model="llama3.1-8b", 
            messages=[
                {"role": "system", "content": "Return ONLY a JSON array of objects: {'f': 'food', 'c': calories, 'ft': fat, 'gi': 'Low/Med/High'}"},
                {"role": "user", "content": f"Analyze this menu text: {extracted_text}"}
            ]
        )
        
        # Clean JSON markdown blocks
        content = analysis_response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Return structured data to the React frontend
        return jsonify(json.loads(content))

    except Exception as e:
        return jsonify({"error": "Failed to process image", "details": str(e)}), 500

#No need for Vercel
if __name__ == '__main__':
    app.run(debug=True, port=5000)