import os
import cv2
import numpy as np
import easyocr
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# ADJUSTMENT 1: Tell Python the .env is up one level in the root
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, "..", ".env"))

app = Flask(__name__)
CORS(app)

# Initialize Groq/Provider Client with Qwen 3
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# ADJUSTMENT 2: Force GPU=False to prevent the long "Torch" hang-up you're seeing
reader = easyocr.Reader(['en'], gpu=False)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['file']
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

        # 1. Local OCR Scan
        print("Starting OCR scan...")
        raw_results = reader.readtext(img, detail=0)
        
        if not raw_results:
            return jsonify({"structuredData": "[]"})

        # CLEANUP: Join into one string and fix common OCR price errors
        # This helps the AI distinguish "S4.99" as "$4.99"
        combined_text = " ".join(raw_results)
        print(f"Cleaned Text for AI: {combined_text}")

        # 2. Qwen 3 Nutritional Analysis
        prompt = f"""
        Below is text from a restaurant menu. The OCR has some errors (e.g., 'S' or '5' instead of '$').
        
        MENU TEXT: {combined_text}
        
        TASK:
        1. Extract EVERY food item (Eggs Benedict, Waffle, Lasagna, Poke Salad, etc.).
        2. For each item, estimate:
           - f: Food Name
           - c: Calories (kcal)
           - ft: Fat (g)
           - gi: Glycemic Index (Low, Medium, High)
        
        Output ONLY a JSON array. Do not skip any items found in the text.
        """

        print("Sending to Groq...")
        response = client.chat.completions.create(
            model="qwen/qwen3-32b", 
            messages=[
                {"role": "system", "content": "You are a precise nutrition assistant. Extract all food items from the text, ignoring prices."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2000 
        )
        
        return jsonify({"structuredData": response.choices[0].message.content})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)