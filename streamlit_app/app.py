import streamlit as st
import requests
import speech_recognition as sr
import pyttsx3
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os

st.set_page_config(page_title="🎙️ Morning Market Brief Assistant")
st.title("🎙️ Morning Market Brief Assistant")

# Global mute toggle
mute_speech = st.checkbox("🔇 Mute Voice Output", value=False)

# TTS function
def speak(text):
    if not mute_speech:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

# Voice input using sounddevice instead of pyaudio
def get_voice_input():
    recognizer = sr.Recognizer()
    fs = 16000  # Sample rate
    seconds = 15  # Duration of recording

    st.info("🎤 Listening... Please speak your query.")
    try:
        # Record audio using sounddevice
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # Wait for recording to finish
        wav_path = "temp_voice.wav"
        write(wav_path, fs, recording)

        # Use the audio file with speech_recognition
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
            st.success("✅ Voice captured. Transcribing...")
            text = recognizer.recognize_google(audio)

        os.remove(wav_path)
        return text

    except sr.UnknownValueError:
        st.error("⚠️ Could not understand audio.")
        return None
    except sr.RequestError:
        st.error("⚠️ API unavailable or quota exceeded.")
        return None
    except Exception as e:
        st.error(f"❌ Could not transcribe audio: {e}")
        return None

# Choose input method
input_method = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Upload Voice"])

query = ""

# Text input mode
if input_method == "⌨️ Text":
    query = st.text_input("Enter your market question")
    if st.button("Get Market Brief (Text)") and query:
        with st.spinner("🔄 Fetching brief..."):
            try:
                response = requests.get(f"http://localhost:8000/brief?query={query}")
                response.raise_for_status()
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

# Voice input mode (record and transcribe)
elif input_method == "🎙️ Upload Voice":
    if st.button("🎤 Record and Transcribe"):
        query = get_voice_input()
        if query:
            st.success(f"📝 Transcribed: {query}")
            with st.spinner("🔄 Fetching market brief..."):
                try:
                    response = requests.get(f"http://localhost:8000/brief?query={query}")
                    response.raise_for_status()
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
        else:
            st.warning("⚠️ No voice input detected. Try again.")
