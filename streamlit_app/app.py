import streamlit as st
import requests
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import queue
import av
import tempfile

st.title("🎙️ Finance Voice/Text Assistant")

# Option to choose input mode
input_mode = st.radio("Select input method:", ["🎤 Speak", "⌨️ Type"])

# Function to send query to backend
def send_query(text):
    response = requests.post("http://localhost:8000/text-query", json={"query": text})
    if response.ok:
        st.success("Response:")
        st.write(response.json()["text"])
    else:
        st.error("Failed to process the query.")

# Text input mode
if input_mode == "⌨️ Type":
    user_input = st.text_input("Enter your financial question:")
    if st.button("Submit"):
        send_query(user_input)

# Voice input mode
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

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                wav_path = f.name

            files = {"audio": open(wav_path, "rb")}
            response = requests.post("http://localhost:8000/voice-query", files=files)
            if response.ok:
                st.success("Response:")
                st.write(response.json()["text"])
            else:
                st.error("Failed to process voice query.")
