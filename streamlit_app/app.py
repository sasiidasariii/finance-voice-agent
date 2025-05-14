import streamlit as st
import requests
import os
import tempfile
import st_audiorec
import speech_recognition as sr
from gtts import gTTS
import threading

# Page Config
st.set_page_config(page_title="🎙️ Finance Assistant")
st.title("🎙️ Morning Market Brief Assistant")

# Init session state
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "audio_ready" not in st.session_state:
    st.session_state.audio_ready = False

# Mute option
st.checkbox("🔇 Mute Voice Output", value=False, key="mute")

# ------------------- TTS -------------------
def speak(text):
    if not st.session_state.get("mute", False):
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tts.save(tmpfile.name)
            with open(tmpfile.name, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# ------------------- Transcription -------------------
def transcribe_audio(wav_audio_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        audio_path = tmpfile.name

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        st.warning("⚠️ Could not understand your voice.")
    except sr.RequestError:
        st.error("❌ Speech-to-text API error.")
    finally:
        os.remove(audio_path)
    return None

# ------------------- Market Brief -------------------
def fetch_market_brief(query):
    try:
        url = f"https://8f72-2409-40f0-1f-32b2-ec80-3655-f9b3-d72b.ngrok-free.app/brief?query={query}"
        res = requests.get(url)
        if res.status_code == 200 and "brief" in res.json():
            brief = res.json()["brief"]
            st.subheader("📄 Market Brief")
            st.write(brief)
            speak(brief)
        else:
            st.error("❌ No brief found.")
    except Exception as e:
        st.error(f"❌ API error: {e}")

# ------------------- Process Audio in Background -------------------
def process_audio(wav_audio):
    # Transcribe the audio in a background thread
    transcribed_text = transcribe_audio(wav_audio)
    if transcribed_text:
        st.session_state.transcribed_text = transcribed_text
        st.success(f"📝 You said: *{transcribed_text}*")
        with st.spinner("📈 Fetching market brief..."):
            fetch_market_brief(transcribed_text)
    else:
        st.warning("⚠️ Could not transcribe.")

# ------------------- Input Mode -------------------
input_mode = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Voice"])

if input_mode == "⌨️ Text":
    query = st.text_input("Enter your market question:")
    if st.button("🟢 Get Market Brief") and query:
        with st.spinner("📈 Fetching market brief..."):
            fetch_market_brief(query)

else:
    st.info("🎧 Click 'Start recording', speak, then click 'Stop'.")
    wav_audio = st_audiorec.st_audiorec()

    if wav_audio and not st.session_state.audio_ready:
        st.session_state.audio_ready = True
        with st.spinner("🔍 Transcribing your voice..."):
            # Start transcription in a separate thread to avoid blocking
            threading.Thread(target=process_audio, args=(wav_audio,)).start()

    if st.session_state.audio_ready:
        st.info("🎧 Transcribing your speech... please wait.")
