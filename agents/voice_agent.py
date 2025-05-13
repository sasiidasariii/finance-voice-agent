# agents/voice_agent.py

import whisper
import pyttsx3
import os

# Load the model once (only when this module is used)
_model = None

def load_whisper_model():
    global _model
    if _model is None:
        try:
            _model = whisper.load_model("base")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    return _model

def speech_to_text(audio_path: str) -> str:
    model = load_whisper_model()
    try:
        result = model.transcribe(audio_path)
        return result['text']
    except Exception as e:
        return f"[ERROR] Could not transcribe: {e}"

def text_to_speech(text: str):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[ERROR] Text-to-speech failed: {e}")
