import streamlit as st
import requests
import speech_recognition as sr
import pyttsx3
import time

st.set_page_config(page_title="Finance Voice Agent")
st.title("🧠🎙️ Finance Voice Agent")

# TTS function
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Voice input via mic
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now.")
        try:
            audio = recognizer.listen(source, timeout=5)  # 5-second timeout
            st.success("✅ Got your voice input. Transcribing...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.error("⚠️ Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            st.error("⚠️ Speech recognition service error.")
            return None
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return None

# Choose input method
input_method = st.radio("Choose input method:", ["🎙️ Voice", "⌨️ Text"])

query = ""
if input_method == "⌨️ Text":
    query = st.text_input("Enter your market question")
    if st.button("Get Brief (Text)") and query:
        with st.spinner("🔄 Fetching brief..."):
            try:
                response = requests.get(f"http://localhost:8000/brief?query={query}")
                response.raise_for_status()
                data = response.json()
                if "summary" in data:
                    summary = data["summary"]
                    st.subheader("📄 Summary")
                    st.write(summary)
                    speak(summary)
                else:
                    st.error(f"⚠️ API Error: {data.get('error', 'No summary returned')}")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Request failed: {e}")
            except ValueError:
                st.error(f"❌ Invalid JSON response: {response.text}")

elif input_method == "🎙️ Voice":
    if st.button("Start Listening"):
        query = get_voice_input()
        if query:
            st.write("📝 Transcribed:", query)
            with st.spinner("🔄 Fetching brief..."):
                try:
                    response = requests.get(f"http://localhost:8000/brief?query={query}")
                    response.raise_for_status()
                    data = response.json()
                    if "summary" in data:
                        summary = data["summary"]
                        st.subheader("📄 Summary")
                        st.write(summary)
                        speak(summary)
                    else:
                        st.error(f"⚠️ API Error: {data.get('error', 'No summary returned')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Request failed: {e}")
                except ValueError:
                    st.error(f"❌ Invalid JSON response: {response.text}")
        else:
            st.error("⚠️ Please speak clearly for better recognition.")
