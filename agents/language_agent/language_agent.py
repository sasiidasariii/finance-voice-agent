from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()  # Load variables from .env file
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

def generate_market_brief(context):
    prompt = f"""
Summarize the following market data in a concise morning brief suitable for a portfolio manager:

{context}

Keep it under 3 sentences, focus on Asia tech stocks.
"""
    response = model.generate_content(prompt)
    return response.text
