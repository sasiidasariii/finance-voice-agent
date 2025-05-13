import streamlit as st
import requests
import pyttsx3
import os
import st_audiorec
import tempfile
import speech_recognition as sr

# ------------------- Page Config ------------------- #
st.set_page_config(page_title="🎙️ Finance Assistant")
st.title("🎙️ Morning Market Brief Assistant")

mute_speech = st.checkbox("🔇 Mute Voice Output", value=False)

# ------------------- TTS ------------------- #
def speak(text):
    """Convert text to speech."""
    if not mute_speech:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

# ------------------- Audio Transcription ------------------- #
def transcribe_audio(wav_audio_data):
    """Save recorded audio and transcribe it using SpeechRecognition."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        tmpfile_path = tmpfile.name

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(tmpfile_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("⚠️ Could not understand audio.")
    except sr.RequestError:
        st.error("⚠️ API unavailable or quota exceeded.")
    finally:
        os.remove(tmpfile_path)
    return None

# ------------------- Audio Input ------------------- #
def get_browser_audio_input():
    """Capture and transcribe audio via browser."""
    st.markdown("#### 🎤 Press the button to talk:")
    wav_audio_data = st_audiorec.st_audiorec()
    
    if wav_audio_data is not None:
        st.info("🛠️ Transcribing your voice...")
        return transcribe_audio(wav_audio_data)
    
    return None

# ------------------- Market Brief Request ------------------- #
def fetch_market_brief(query):
    """Fetch market brief from backend."""
    try:
        FASTAPI_URL = "https://finance-voice-agent.onrender.com" 
        response = requests.get(f"{FASTAPI_URL}/brief?query={query}")
        
        # Log the raw response to inspect its contents
        st.write(f"Raw response: {response.text}")

        # Check if the response is valid JSON
        data = response.json()
        brief = data.get("brief")
        if brief:
            st.subheader("📄 Market Brief")
            st.write(brief)
            speak(brief)
        else:
            st.error("⚠️ No brief returned.")
    except Exception as e:
        st.error(f"❌ Error: {e}")


# ------------------- UI: Input Method ------------------- #
input_method = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Voice"])

# ----- Text Mode ----- #
if input_method == "⌨️ Text":
    query = st.text_input("Enter your market question:")
    if st.button("🟢 Get Market Brief") and query:
        with st.spinner("🔄 Fetching market brief..."):
            fetch_market_brief(query)

# ----- Voice Mode ----- #
elif input_method == "🎙️ Voice":
    st.info("🎧 Click the start recording button below, speak clearly, then stop.")
    transcribed_text = get_browser_audio_input()
    if transcribed_text:
        st.success(f"📝 You said: _{transcribed_text}_")
        with st.spinner("🔄 Fetching market brief..."):
            fetch_market_brief(transcribed_text)
