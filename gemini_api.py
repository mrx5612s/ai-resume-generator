import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
def generate_with_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, json=payload)
    result = response.json()
    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return f"⚠️ Gemini API error: {result}"
