import whisper
import logging
import pyttsx3  # For Text-to-Speech conversion

# Initialize the Whisper model
model = whisper.load_model("base")

# Initialize Text-to-Speech engine (TTS)
tts_engine = pyttsx3.init()

# Set up logging for debugging purposes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe(audio_file_path):
    """
    Transcribes audio to text using Whisper model.
    """
    try:
        logger.info(f"Transcribing audio from: {audio_file_path}")
        result = model.transcribe(audio_file_path)
        transcribed_text = result['text']
        logger.info(f"Transcription result: {transcribed_text}")
        return transcribed_text
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return "Error: Failed to transcribe audio."

def speak_text(text):
    """
    Converts text to speech using pyttsx3 and plays the result.
    """
    try:
        logger.info(f"Converting text to speech: {text}")
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        logger.error(f"Error during text-to-speech conversion: {e}")

# Example usage:
if __name__ == "__main__":
    # Example: Transcribe an audio file and then speak the response
    audio_path = "path_to_audio_file.wav"  # Provide the correct path to the audio file
    transcribed_text = transcribe(audio_path)
    
    # You would pass this transcribed text to another agent for processing
    logger.info(f"Transcribed Text: {transcribed_text}")
    
    # Convert the response back to speech
    speak_text(f"Your transcribed text is: {transcribed_text}")
