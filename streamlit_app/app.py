import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import numpy as np
import queue
import threading
import tempfile
import wave
import speech_recognition as sr
import os
from gtts import gTTS

# Page config
st.set_page_config(page_title="🎙️ Finance Assistant")
st.title("🎙️ Morning Market Brief Assistant")

# Session state init
if "recorded_frames" not in st.session_state:
    st.session_state.recorded_frames = []
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "mute" not in st.session_state:
    st.session_state.mute = False

st.checkbox("🔇 Mute Voice Output", value=st.session_state.mute, key="mute")

# Text-to-Speech
def speak(text):
    if not st.session_state.mute:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tts.save(tmpfile.name)
            with open(tmpfile.name, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# Fetch brief
def fetch_market_brief(query):
    try:
        url = f"https://your-api-url.com/brief?query={query}"
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

# Convert audio frames to .wav and transcribe
def convert_and_transcribe(frames, sample_rate):
    audio_data = np.concatenate(frames, axis=1).flatten().astype(np.int16)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
        with wave.open(wav_file.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file.name) as source:
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio)
                st.success(f"📝 You said: *{text}*")
                fetch_market_brief(text)
            except sr.UnknownValueError:
                st.warning("⚠️ Could not understand audio.")
            except sr.RequestError:
                st.error("❌ Google API error.")
            finally:
                os.remove(wav_file.name)

# WebRTC audio handler
audio_q = queue.Queue()

def audio_callback(frame: av.AudioFrame) -> av.AudioFrame:
    pcm = frame.to_ndarray()
    audio_q.put(pcm)
    return frame

# Trigger for stop button
if "stop_triggered" not in st.session_state:
    st.session_state.stop_triggered = False

# Start webrtc
ctx = webrtc_streamer(
    key="sendonly-audio",
    mode=WebRtcMode.SENDONLY,
    audio_frame_callback=audio_callback,
    media_stream_constraints={"audio": True, "video": False},
)

# Record and buffer audio frames
if ctx.state.playing:
    st.info("🎙️ Recording... Speak now. Click 'Stop Recording' when done.")
    if st.button("⏹️ Stop Recording"):
        st.session_state.stop_triggered = True

    if not st.session_state.stop_triggered:
        while not audio_q.empty():
            pcm = audio_q.get()
            st.session_state.recorded_frames.append(pcm)

# On stop: process audio
if st.session_state.stop_triggered and st.session_state.recorded_frames:
    with st.spinner("🔍 Transcribing your voice..."):
        convert_and_transcribe(st.session_state.recorded_frames, sample_rate=48000)

    # Reset
    st.session_state.recorded_frames = []
    st.session_state.stop_triggered = False
