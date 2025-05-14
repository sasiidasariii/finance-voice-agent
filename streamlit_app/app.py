import streamlit as st
import requests
import os
import tempfile
import st_audiorec
import speech_recognition as sr
from gtts import gTTS

# Set up session state for managing audio state and processing flow
if "audio_ready" not in st.session_state:
    st.session_state.audio_ready = False
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "processing" not in st.session_state:
    st.session_state.processing = False

# ------------------- TTS -------------------
def speak(text):
    """Convert text to speech using gTTS and play in the browser."""
    if not st.session_state.get("mute", False):
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tts.save(tmpfile.name)
            with open(tmpfile.name, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# ------------------- Transcription -------------------
def transcribe_audio(wav_audio_data):
    """Transcribe the recorded audio to text."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        audio_path = tmpfile.name

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)  # Only record a chunk of the audio to speed up process
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "⚠️ Could not understand your voice."
    except sr.RequestError:
        return "❌ Speech-to-text API error."
    finally:
        os.remove(audio_path)
    return None

# ------------------- Market Brief Request -------------------
def fetch_market_brief(query):
    """Fetch market brief from backend API."""
    try:
        url = f"https://8f72-2409-40f0-1f-32b2-ec80-3655-f9b3-d72b.ngrok-free.app/brief?query={query}"
        response = requests.get(url)

        if response.status_code == 200:
            try:
                data = response.json()
                brief = data.get("brief")
                if brief:
                    st.subheader("📄 Market Brief")
                    st.write(brief)
                    speak(brief)
                else:
                    st.error("⚠️ No brief returned.")
            except Exception as json_err:
                st.error(f"⚠️ Error parsing JSON: {json_err}")
        else:
            st.error(f"❌ API error: Status code {response.status_code}")
    except Exception as e:
        st.error(f"❌ Request error: {e}")

# ------------------- UI: Input Method -------------------
st.set_page_config(page_title="🎙️ Finance Assistant")
st.title("🎙️ Morning Market Brief Assistant")
input_method = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Voice"])

if input_method == "⌨️ Text":
    st.subheader("📍 Enter your market query:")
    query = st.text_input("Enter your market question:")
    if st.button("🟢 Get Market Brief") and query:
        with st.spinner("📈 Fetching market brief..."):
            fetch_market_brief(query)

else:
    st.subheader("🎤 Speak your market query:")
    st.info("🎧 Click 'Start recording', speak, and then click 'Stop' to transcribe.")

    # Audio recording and transcribing after Stop button is clicked
    wav_audio = st_audiorec.st_audiorec()

    # After recording, audio is ready in next run
    if wav_audio and not st.session_state.audio_ready:
        st.session_state.audio_ready = True
        st.experimental_rerun()  # Trigger a rerun to get audio ready

    # Process the audio if ready
    if st.session_state.audio_ready and not st.session_state.processing:
        st.session_state.processing = True
        with st.spinner("🛠️ Transcribing your voice..."):
            st.session_state.transcribed_text = transcribe_audio(wav_audio)
        st.experimental_rerun()  # Re-run after transcription

    # Show transcribed text once available
    if st.session_state.transcribed_text:
        st.success(f"📝 You said: *{st.session_state.transcribed_text}*")
        with st.spinner("📈 Fetching market brief..."):
            fetch_market_brief(st.session_state.transcribed_text)
        # Reset for next round
        st.session_state.audio_ready = False
        st.session_state.processing = False
        st.session_state.transcribed_text = ""
