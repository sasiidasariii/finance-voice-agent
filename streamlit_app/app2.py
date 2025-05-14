import streamlit as st
import requests
import speech_recognition as sr
import sounddevice as sd
from scipy.io.wavfile import write
import os
from audio_controller import audio  # Uses gTTS and returns MP3 path

st.set_page_config(page_title="🎙️ Morning Market Brief Assistant")
st.title("🎙️ Morning Market Brief Assistant")

# Initialize session state
if "brief" not in st.session_state:
    st.session_state.brief = ""
if "query" not in st.session_state:
    st.session_state.query = ""
if "audio_path" not in st.session_state:
    st.session_state.audio_path = ""

# Voice input using sounddevice
def get_voice_input():
    recognizer = sr.Recognizer()
    fs = 16000  # Sample rate
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

# Input method
input_method = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Record Voice"])

# Text input
if input_method == "⌨️ Text":
    st.session_state.query = st.text_input("Enter your market question", value=st.session_state.query)
    if st.button("Get Market Brief (Text)") and st.session_state.query:
        with st.spinner("🔄 Fetching brief..."):
            try:
                response = requests.get(f"https://8f72-2409-40f0-1f-32b2-ec80-3655-f9b3-d72b.ngrok-free.app/brief?query={st.session_state.query}")
                response.raise_for_status()
                data = response.json()
                st.session_state.brief = data.get("brief", "")
                st.session_state.audio_path = audio.generate_audio(st.session_state.brief)
            except Exception as e:
                st.error(f"❌ Error: {e}")

# Voice input
elif input_method == "🎙️ Record Voice":
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

# Display brief and audio
if st.session_state.brief:
    st.subheader("📄 Market Brief")
    st.write(st.session_state.brief)

    if st.session_state.audio_path:
        with open(st.session_state.audio_path, "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3", start_time=0)