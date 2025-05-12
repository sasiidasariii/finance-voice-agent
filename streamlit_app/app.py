import streamlit as st
import requests

st.title("🎙️ Finance Voice Assistant")

uploaded_file = st.file_uploader("Upload your voice query (.wav)", type=["wav"])
if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("Send Query"):
        response = requests.post(
            "http://localhost:8000/voice-query",
            files={"audio": uploaded_file.getvalue()}
        )
        if response.ok:
            st.success("Response:")
            st.write(response.json()["text"])
        else:
            st.error("Failed to process the query.")
