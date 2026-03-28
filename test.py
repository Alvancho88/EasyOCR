import os
import time
from google import genai  # This is the NEW 2026 way
from dotenv import load_dotenv

load_dotenv()

# Force v1 for stability
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options={'api_version': 'v1'}
)

# 2026 Free Tier Models to try in order
models_to_test = [
    "gemini-2.5-flash-lite", 
    "gemini-2.5-flash", 
    "gemini-1.5-flash-8b"
]

for model_name in models_to_test:
    print(f"--- Testing Model: {model_name} ---")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Hello! Are you active on my free tier?"
        )
        print(f"SUCCESS with {model_name}!")
        print(f"Response: {response.text}")
        break # Stop once one works!
    except Exception as e:
        if "429" in str(e):
            print(f"Quota issue with {model_name}. Waiting 10s...")
            time.sleep(10)
        else:
            print(f"Failed with {model_name}: {e}")

print("\nTests complete.")