import os
import requests
import streamlit as st
import speech_recognition as sr

# Detect if running on Streamlit Cloud
IS_CLOUD = os.getenv("STREAMLIT_CLOUD", "0") == "1"

# Conditionally import audio features
if not IS_CLOUD:
    import sounddevice as sd
    from scipy.io.wavfile import write
    from audio_controller import audio
    import pyttsx3

# Page Setup
st.set_page_config(page_title="🎙️ Morning Market Brief Assistant")
st.title("🎙️ Morning Market Brief Assistant")

# Session State Init
if "brief" not in st.session_state:
    st.session_state.brief = ""
if "query" not in st.session_state:
    st.session_state.query = ""

# Optional TTS
def speak(text):
    if not IS_CLOUD:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

# Voice input via microphone
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

# Input choice
input_method = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Record Voice" if not IS_CLOUD else "🎙️ Voice (Unavailable in Cloud)"])

# Text Input Path
if input_method == "⌨️ Text":
    st.session_state.query = st.text_input("Enter your market question", value=st.session_state.query)
    if st.button("Get Market Brief (Text)") and st.session_state.query:
        with st.spinner("🔄 Fetching brief..."):
            try:
                response = requests.get(f"http://localhost:8000/brief?query={st.session_state.query}")
                response.raise_for_status()
                st.session_state.brief = response.json().get("brief", "")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# Voice Input Path
elif input_method.startswith("🎙️ Record Voice") and not IS_CLOUD:
    if st.button("🎤 Record and Transcribe"):
        query = get_voice_input()
        if query:
            st.success(f"📝 Transcribed: {query}")
            st.session_state.query = query
            with st.spinner("🔄 Fetching market brief..."):
                try:
                    response = requests.get(f"http://localhost:8000/brief?query={query}")
                    response.raise_for_status()
                    st.session_state.brief = response.json().get("brief", "")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Voice unavailable warning (on cloud)
elif IS_CLOUD and input_method.startswith("🎙️"):
    st.warning("⚠️ Voice input is disabled on Streamlit Cloud. Please use text input.")

# Display market brief
if st.session_state.brief:
    st.subheader("📄 Market Brief")
    st.write(st.session_state.brief)

    # Local: Voice control
    if not IS_CLOUD:
        if st.button("▶️ Play Voice"):
            audio.play(st.session_state.brief)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⏸️ Pause"):
                audio.pause()
        with col2:
            if st.button("⏯️ Resume"):
                audio.resume()
        with col3:
            if st.button("⏹️ Stop"):
                audio.stop()
    else:
        st.info("🔈 Text-to-speech & playback available in local version.")
