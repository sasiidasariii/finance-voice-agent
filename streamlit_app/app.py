import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import speech_recognition as sr
import queue
import threading
import requests
from gtts import gTTS
import tempfile
import os

st.set_page_config(page_title="🎙️ Finance Assistant")
st.title("🎙️ Morning Market Brief Assistant")

# Session state
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""

if "mute" not in st.session_state:
    st.session_state.mute = False

st.checkbox("🔇 Mute Voice Output", value=st.session_state.mute, key="mute")

# TTS
def speak(text):
    if not st.session_state.get("mute", False):
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tts.save(tmpfile.name)
            with open(tmpfile.name, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# Market Brief API
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

# Audio queue and processing
audio_queue = queue.Queue()

def process_audio_stream():
    recognizer = sr.Recognizer()
    while True:
        frame = audio_queue.get()
        if frame is None:
            break
        try:
            audio_data = frame.to_ndarray().tobytes()
            audio = sr.AudioData(audio_data, frame.sample_rate, 2)
            text = recognizer.recognize_google(audio)
            if text:
                st.session_state.transcribed_text += " " + text
                st.success(f"📝 You said: *{st.session_state.transcribed_text.strip()}*")
                fetch_market_brief(st.session_state.transcribed_text.strip())
                st.session_state.transcribed_text = ""  # reset after use
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            st.error(f"Speech recognition API error: {e}")

threading.Thread(target=process_audio_stream, daemon=True).start()

# Audio callback
def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio_queue.put(frame)
    return frame

# UI
input_mode = st.radio("Choose input method:", ["⌨️ Text", "🎙️ Voice"])

if input_mode == "⌨️ Text":
    query = st.text_input("Enter your market question:")
    if st.button("🟢 Get Market Brief") and query:
        with st.spinner("📈 Fetching market brief..."):
            fetch_market_brief(query)
else:
    st.info("🎧 Speak into your mic. It will transcribe and fetch a market brief.")
    webrtc_streamer(
        key="realtime-audio",
        mode=WebRtcMode.SENDONLY,
        audio_frame_callback=audio_frame_callback,
        media_stream_constraints={"video": False, "audio": True}
    )
