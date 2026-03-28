import os
import cv2
import numpy as np
import easyocr
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
app = Flask(__name__)
CORS(app)

# Initialize Groq/Provider Client with Qwen 3
client = OpenAI(
    base_url="https://api.groq.com/openai/v1", # Ensure this matches your provider's URL
    api_key=os.getenv("GROQ_API_KEY")
)

reader = easyocr.Reader(['en'], gpu=False)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['file']
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

        # 1. Local OCR Scan
        raw_results = reader.readtext(img, detail=0, paragraph=True)
        if not raw_results:
            return jsonify({"structuredData": "[]"})

        # 2. Qwen 3 Nutritional Analysis
        # We ask for GI and Fat specifically for senior health tracking
        prompt = f"""
        Extract menu items from this text: {raw_results}
        For each item, provide:
        - f: Food Name
        - c: Estimated Calories (kcal)
        - ft: Estimated Fat (g)
        - gi: Glycemic Index Category (Low, Medium, High)
        
        Output ONLY a JSON array of objects.
        """

        response = client.chat.completions.create(
            model="qwen/qwen3-32b", # Using the model from your 2026 list
            messages=[
                {"role": "system", "content": "You are a senior-health nutrition expert. Output strictly JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return jsonify({"structuredData": response.choices[0].message.content})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)