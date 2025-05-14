import os
import streamlit as st
import requests
import speech_recognition as sr

# Detect if running in Streamlit Cloud
IS_CLOUD = os.getenv("STREAMLIT_CLOUD", "0") == "1"

if not IS_CLOUD:
    import sounddevice as sd
    from scipy.io.wavfile import write

from audio_controller import audio  # Uses gTTS and returns MP3 path

st.set_page_config(page_title="🎙️ Morning Market Brief Assistant")
st.title("🎙️ Morning Market Brief Assistant")

# Session State
if "brief" not in st.session_state:
    st.session_state.brief = ""
if "query" not in st.session_state:
    st.session_state.query = ""
if "audio_path" not in st.session_state:
    st.session_state.audio_path = ""

# Voice input
def get_voice_input():
    recognizer = sr.Recognizer()
    fs = 16000
    seconds = 15

    st.info("🎤 Listening... Please speak your query.")
    try:
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        wav_path = "temp_voice.wav"
        write(wav_path, fs, recording)

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            st.success("✅ Voice captured. Transcribing...")
            text = recognizer.recognize_google(audio_data)

        os.remove(wav_path)
        return text

    except sr.UnknownValueError:
        st.error("⚠️ Could not understand audio.")
    except sr.RequestError:
        st.error("⚠️ API unavailable or quota exceeded.")
    except Exception as e:
        st.error(f"❌ Transcription error: {e}")
    return None

# Input method selection
input_method = st.radio("Choose input method:", ["⌨️ Text"] + ([] if IS_CLOUD else ["🎙️ Record Voice"]))

# Text input
if input_method == "⌨️ Text":
    st.session_state.query = st.text_input("Enter your market question", value=st.session_state.query)
    if st.button("Get Market Brief (Text)") and st.session_state.query:
        with st.spinner("🔄 Fetching brief..."):
            try:
                response = requests.get(f"http://localhost:8000/brief?query={st.session_state.query}")
                response.raise_for_status()
                data = response.json()
                st.session_state.brief = data.get("brief", "")
                st.session_state.audio_path = audio.generate_audio(st.session_state.brief)
            except Exception as e:
                st.error(f"❌ Error: {e}")

# Voice input (local only)
elif input_method == "🎙️ Record Voice" and not IS_CLOUD:
    if st.button("🎤 Record and Transcribe"):
        query = get_voice_input()
        if query:
            st.success(f"📝 Transcribed: {query}")
            st.session_state.query = query
            with st.spinner("🔄 Fetching market brief..."):
                try:
                    response = requests.get(f"http://localhost:8000/brief?query={query}")
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.brief = data.get("brief", "")
                    st.session_state.audio_path = audio.generate_audio(st.session_state.brief)
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Cloud: Voice not supported message
if IS_CLOUD and input_method == "🎙️ Record Voice":
    st.warning("⚠️ Voice input is disabled on Streamlit Cloud. Please run locally for full voice support.")

# Output
if st.session_state.brief:
    st.subheader("📄 Market Brief")
    st.write(st.session_state.brief)

    if st.session_state.audio_path:
        with open(st.session_state.audio_path, "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
