import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


try:
    model = genai.GenerativeModel(model_name='models/gemini-1.5-flash-latest')
    print("[DEBUG] Gemini 1.5 Flash model loaded successfully.")
except Exception as e:
    print(f"[ERROR] Gemini 1.5 Flash is not available: {e}")
    model = None  

def generate_brief(prompt: str):
    try:
        print(f"[DEBUG] Using model: {model._model_name}")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[ERROR] Failed to generate content: {e}")
        return None
