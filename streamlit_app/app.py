import streamlit as st
import requests
import pyttsx3
import os
import st_audiorec
import tempfile
import speech_recognition as sr

st.set_page_config(page_title="🎙️ Morning Market Brief Assistant")
st.title("🎙️ Morning Market Brief Assistant")

mute_speech = st.checkbox("🔇 Mute Voice Output", value=False)

def speak(text):
    if not mute_speech:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

# Use st_audiorec for browser-based recording
def get_browser_audio_input():
    wav_audio_data = st_audiorec.st_audiorec()
    if wav_audio_data is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(wav_audio_data)
            tmpfile_path = tmpfile.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(tmpfile_path) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.error("⚠️ Could not understand audio.")
        except sr.RequestError:
            st.error("⚠️ API unavailable or quota exceeded.")
        finally:
            os.remove(tmpfile_path)
    return None

# Input method selection
input_method = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Voice"])

query = ""

if input_method == "⌨️ Text":
    query = st.text_input("Enter your market question")
    if st.button("Get Market Brief (Text)") and query:
        with st.spinner("🔄 Fetching brief..."):
            try:
                response = requests.get(f"http://localhost:8000/brief?query={query}")
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

elif input_method == "🎙️ Voice":
    st.info("🎤 Record your voice below:")
    transcribed_text = get_browser_audio_input()
    if transcribed_text:
        st.success(f"📝 Transcribed: {transcribed_text}")
        with st.spinner("🔄 Fetching market brief..."):
            try:
                response = requests.get(f"http://localhost:8000/brief?query={transcribed_text}")
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
