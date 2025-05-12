from fastapi import FastAPI, UploadFile
from agents.voice_agent.voice_agent import transcribe_audio, speak_text
from agents.api_agent.api_agent import get_stock_data
from agents.language_agent.language_agent import generate_market_brief
import tempfile

app = FastAPI()

@app.post("/voice-query")
async def handle_query(audio: UploadFile):
    # Save uploaded audio file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(await audio.read())
        temp_audio_path = temp_audio.name

    # Convert voice to text
    question = transcribe_audio(temp_audio_path)

    # Get stock data (example: TSMC, Samsung)
    tsmc = get_stock_data("TSM")
    samsung = get_stock_data("005930.KS")
    
    context = f"TSMC closing price: {tsmc['close']}, change: {tsmc['change']}%.\n" \
              f"Samsung closing price: {samsung['close']}, change: {samsung['change']}%."

    # Generate response using Gemini
    summary = generate_market_brief(context)

    # Speak the result
    speak_text(summary)

    return {"text": summary}
