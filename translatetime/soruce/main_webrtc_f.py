import logging
import queue
from io import BytesIO
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import av

# Set up logging
logger = logging.getLogger(__name__)
translator = Translator()

# Mapping language names to codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

# Translate speech
def translate_text(text, src_lang, dest_lang):
    try:
        translated = translator.translate(text, src=src_lang, dest=dest_lang)
        return translated.text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return "Translation Error"

# Convert text to speech and play
def text_to_speech(text, language):
    speech = gTTS(text=text, lang=language, slow=False)
    speech_buffer = BytesIO()
    speech.write_to_fp(speech_buffer)
    speech_buffer.seek(0)
    return speech_buffer

# Speech recognition callback
result_queue = queue.Queue()

def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    recognizer = sr.Recognizer()
    audio_data = frame.to_ndarray()

    with sr.AudioFile(BytesIO(audio_data)) as source:
        try:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=st.session_state.from_language)
            result_queue.put(text)
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")

    return frame

# UI layout
st.title("🗣️ Real-time Voice Translator")

# Language selection
from_language_name = st.selectbox("Select Source Language:", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index("english"))
to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index("spanish"))

# Store language codes
st.session_state.from_language = get_language_code(from_language_name)
st.session_state.to_language = get_language_code(to_language_name)

if "isTranslating" not in st.session_state:
    st.session_state.isTranslating = False

# Start and stop buttons
if st.button("Start Translation"):
    st.session_state.isTranslating = True

if st.button("Stop Translation"):
    st.session_state.isTranslating = False
    st.warning("🛑 Translation Stopped")

if st.session_state.isTranslating:
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDRECV,
        media_stream_constraints={"audio": True, "video": False},
        audio_frame_callback=audio_frame_callback,
        async_processing=True,
    )

    output_placeholder = st.empty()

    while st.session_state.isTranslating:
        if not result_queue.empty():
            recognized_text = result_queue.get()

            if recognized_text:
                output_placeholder.text(f"🗣️ You said: {recognized_text}")

                translated_text = translate_text(recognized_text, st.session_state.from_language, st.session_state.to_language)
                output_placeholder.text(f"🔊 Translation: {translated_text}")

                speech_audio = text_to_speech(translated_text, st.session_state.to_language)
                st.audio(speech_audio, format="audio/mp3")
