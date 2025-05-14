import streamlit as st
import requests
import os
import tempfile
import st_audiorec
import whisper
from gtts import gTTS

# Page Config
st.set_page_config(page_title="🎙️ Finance Assistant")
st.title("🎙️ Morning Market Brief Assistant")

# Init session state
if "audio_ready" not in st.session_state:
    st.session_state.audio_ready = False
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "processing" not in st.session_state:
    st.session_state.processing = False

# Mute option
st.checkbox("🔇 Mute Voice Output", value=False, key="mute")

# Load Whisper model once
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()

# ------------------- TTS -------------------
def speak(text):
    if not st.session_state.get("mute", False):
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tts.save(tmpfile.name)
            with open(tmpfile.name, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# ------------------- Transcription using Whisper -------------------
def transcribe_audio_fast(wav_audio_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        audio_path = tmpfile.name

    try:
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        st.error(f"❌ Transcription error: {e}")
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

# ------------------- Input Mode -------------------
input_mode = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Voice"])

if input_mode == "⌨️ Text":
    query = st.text_input("Enter your market question:")
    if st.button("🟢 Get Market Brief") and query:
        with st.spinner("📈 Fetching market brief..."):
            fetch_market_brief(query)

else:
    st.info("🎧 Click 'Start recording', speak, then click 'Stop' to transcribe.")
    wav_audio = st_audiorec.st_audiorec()

    # After recording, audio is ready in next run
    if wav_audio and not st.session_state.audio_ready:
        st.session_state.audio_ready = True
        st.experimental_rerun()

    if st.session_state.audio_ready and not st.session_state.processing:
        st.session_state.processing = True
        with st.spinner("🛠️ Transcribing your voice..."):
            st.session_state.transcribed_text = transcribe_audio_fast(wav_audio)
        st.experimental_rerun()

    if st.session_state.transcribed_text:
        st.success(f"📝 You said: *{st.session_state.transcribed_text}*")
        with st.spinner("📈 Fetching market brief..."):
            fetch_market_brief(st.session_state.transcribed_text)
        # Reset for next round
        st.session_state.audio_ready = False
        st.session_state.processing = False
        st.session_state.transcribed_text = ""
