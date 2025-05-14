import streamlit as st
import requests
import os
import tempfile
import st_audiorec
import speech_recognition as sr
from gtts import gTTS

# ------------------ Setup ------------------
os.environ["STREAMLIT_CONFIG_DIR"] = "/tmp/.streamlit"
st.set_page_config(page_title="🎙️ Finance Assistant")
st.title("🎙️ Morning Market Brief Assistant")

mute_speech = st.checkbox("🔇 Mute Voice Output", value=False)

# ------------------ Text-to-Speech ------------------
def speak(text):
    if not mute_speech:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tmpfile_path = tmpfile.name
            tts.save(tmpfile_path)
        with open(tmpfile_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")

# ------------------ Transcription ------------------
def transcribe_audio(wav_audio_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        tmpfile_path = tmpfile.name

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(tmpfile_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        st.error("⚠️ Could not understand audio.")
    except sr.RequestError:
        st.error("⚠️ API unavailable or quota exceeded.")
    except Exception as e:
        st.error(f"❌ Transcription error: {e}")
    finally:
        os.remove(tmpfile_path)

    return None

# ------------------ Fetch Brief ------------------
def fetch_market_brief(query):
    try:
        url = f"https://8f72-2409-40f0-1f-32b2-ec80-3655-f9b3-d72b.ngrok-free.app/brief?query={query}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            brief = data.get("brief")
            if brief:
                st.subheader("📄 Market Brief")
                st.write(brief)
                speak(brief)
            else:
                st.error("⚠️ No brief returned.")
        else:
            st.error(f"❌ API error: {response.status_code}")
            st.text(response.text)
    except Exception as e:
        st.error(f"❌ Failed to fetch brief: {e}")

# ------------------ Input UI ------------------
input_method = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Voice"])

if input_method == "⌨️ Text":
    query = st.text_input("Enter your market question:")
    if st.button("🟢 Get Market Brief") and query:
        with st.spinner("🔄 Fetching market brief..."):
            fetch_market_brief(query)

# ------------------ Voice Input Mode ------------------
elif input_method == "🎙️ Voice":
    st.info("🎧 Press 'Start Recording', speak, then 'Stop'. The assistant will respond automatically.")

    if "transcribed" not in st.session_state:
        st.session_state.transcribed = None

    wav_audio_data = st_audiorec.st_audiorec()

    if wav_audio_data is not None and st.session_state.transcribed is None:
        st.audio(wav_audio_data, format="audio/wav")
        with st.spinner("🛠️ Transcribing..."):
            transcribed = transcribe_audio(wav_audio_data)
            if transcribed:
                st.session_state.transcribed = transcribed
                st.success(f"📝 You said: *{transcribed}*")
                with st.spinner("🔄 Fetching market brief..."):
                    fetch_market_brief(transcribed)
