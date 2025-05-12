import streamlit as st
import requests
import queue
import av
import tempfile
from gtts import gTTS
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

st.set_page_config(page_title="Finance Assistant", layout="centered")
st.title("🎙️ Finance Voice/Text Assistant")

# --- Input Mode Selection ---
input_mode = st.radio("Select input method:", ["🎤 Speak", "⌨️ Type"])

# --- Backend URL (use 'backend' in Docker Compose) ---
BACKEND_URL = "http://backend:8000"

# --- TTS Output ---
def speak_response(text):
    tts = gTTS(text=text, lang='en')
    tts_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tts.save(tts_file.name)
    st.audio(tts_file.name, format="audio/mp3")

# --- Send Text Query ---
def send_text_query(text):
    with st.spinner("Processing your text query..."):
        try:
            response = requests.post(f"{BACKEND_URL}/text-query", json={"query": text})
            if response.ok:
                answer = response.json()["text"]
                st.success("Response:")
                st.write(answer)
                speak_response(answer)
            else:
                st.error("❌ Backend failed to process the query.")
        except Exception as e:
            st.error(f"❌ Connection error: {e}")

# --- Send Voice Query ---
def send_voice_query(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        wav_path = f.name

    with open(wav_path, "rb") as f:
        files = {"audio": f}
        with st.spinner("Processing your voice query..."):
            try:
                response = requests.post(f"{BACKEND_URL}/voice-query", files=files)
                if response.ok:
                    answer = response.json()["text"]
                    st.success("Response:")
                    st.write(answer)
                    speak_response(answer)
                else:
                    st.error("❌ Backend failed to process voice query.")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")

# --- Text Input Mode ---
if input_mode == "⌨️ Type":
    user_input = st.text_input("Enter your financial question:")
    if st.button("Submit"):
        if user_input.strip():
            send_text_query(user_input)
        else:
            st.warning("⚠️ Please enter a valid query.")

# --- Voice Input Mode ---
elif input_mode == "🎤 Speak":
    class AudioProcessor(AudioProcessorBase):
        def __init__(self) -> None:
            self.buffer = queue.Queue()

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            audio = frame.to_ndarray().flatten().tobytes()
            self.buffer.put(audio)
            return frame

    ctx = webrtc_streamer(
        key="voice",
        mode="SENDONLY",
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )

    if ctx.audio_processor:
        if st.button("Submit Voice Query"):
            audio_data = b"".join(list(ctx.audio_processor.buffer.queue))
            if not audio_data:
                st.warning("⚠️ No audio captured. Please try again.")
            else:
                send_voice_query(audio_data)
