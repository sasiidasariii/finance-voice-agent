# Speech-to-Text (STT) and Text-to-Speech (TTS)
import whisper
import pyttsx3

# Load Whisper model
model = whisper.load_model("base")

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
