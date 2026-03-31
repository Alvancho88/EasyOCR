import os
import base64
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
from pathlib import Path

# Cloud-safe dotenv loading
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)

app = Flask(__name__)
CORS(app)

groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
cerebras_client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file"}), 400
            
        image_base64 = base64.b64encode(file.read()).decode('utf-8')

        # STAGE 1: OCR
        ocr_res = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "List every food item and price found in this image."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]}]
        )
        text_data = ocr_res.choices[0].message.content

        # STAGE 2: Analysis (More strict prompt to avoid price/calorie confusion)
        analysis_res = cerebras_client.chat.completions.create(
            model="llama3.1-8b", 
            messages=[
                {"role": "system", "content": "You are a nutrition expert. Convert the menu text into a JSON array. DO NOT use prices as calories. Estimate calories based on the dish name. Format: {'f': 'dish', 'c': kcal_estimate, 'ft': fat_g, 'gi': 'Low/Med/High'}"},
                {"role": "user", "content": text_data}
            ]
        )
        
        # Robust JSON extraction
        raw_content = analysis_res.choices[0].message.content
        json_start = raw_content.find('[')
        json_end = raw_content.rfind(']') + 1
        clean_json = raw_content[json_start:json_end]
        
        return jsonify(json.loads(clean_json))

    except Exception as e:
        # This will show up in your Vercel logs so we can see exactly what failed
        print(f"CRITICAL ERROR: {str(e)}")
        return jsonify({"error": "Processing failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)