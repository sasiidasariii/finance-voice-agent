import streamlit as st
import requests
import os
import tempfile
import st_audiorec
import speech_recognition as sr
from gtts import gTTS

# Set custom directory for Streamlit config
os.environ["STREAMLIT_CONFIG_DIR"] = "/tmp/.streamlit"

# ------------------- Page Config -------------------
st.set_page_config(page_title="🎙️ Finance Assistant")
st.title("🎙️ Morning Market Brief Assistant")

mute_speech = st.checkbox("🔇 Mute Voice Output", value=False)

# ------------------- TTS using gTTS -------------------
def speak(text):
    """Convert text to speech using gTTS and play in browser."""
    if not mute_speech:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tmpfile_path = tmpfile.name
            tts.save(tmpfile_path)
        with open(tmpfile_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")

# ------------------- Transcription -------------------
def transcribe_audio(wav_audio_data):
    """Transcribe recorded WAV data using SpeechRecognition."""
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
    except Exception as e:
        st.error(f"❌ Error during transcription: {e}")
    finally:
        os.remove(tmpfile_path)

    return None

# ------------------- Market Brief Request -------------------
def fetch_market_brief(query):
    """Fetch market brief from backend using query."""
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
                st.text(f"Raw response:\n{response.text}")
        else:
            st.error(f"❌ API error: Status code {response.status_code}")
            st.text(f"Response:\n{response.text}")

    except Exception as e:
        st.error(f"❌ Request error: {e}")

# ------------------- Input Method -------------------
input_method = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Voice"])

# ----- Text Input -----
if input_method == "⌨️ Text":
    query = st.text_input("Enter your market question:")
    if st.button("🟢 Get Market Brief") and query:
        with st.spinner("🔄 Fetching market brief..."):
            fetch_market_brief(query)

# ----- Voice Input -----
elif input_method == "🎙️ Voice":
    st.info("🎧 Click 'Start Recording', speak, then click 'Stop' to auto-transcribe and get brief.")
    wav_audio_data = st_audiorec.st_audiorec()

    if wav_audio_data is not None:
        st.audio(wav_audio_data, format='audio/wav')
        st.info("🛠️ Transcribing...")
        transcribed_text = transcribe_audio(wav_audio_data)

        if transcribed_text:
            st.success(f"📝 You said: *{transcribed_text}*")
            with st.spinner("🔄 Fetching market brief..."):
                fetch_market_brief(transcribed_text)
