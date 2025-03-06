import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator
from gtts import gTTS
from io import BytesIO
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av

# Initialize translator
translator = Translator()

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

# Translate the spoken text
def translator_function(spoken_text, from_language, to_language):
    return translator.translate(spoken_text, src=from_language, dest=to_language).text

# Generate and play voice output smoothly using gTTS
def text_to_voice(text_data, to_language):
    tts = gTTS(text=text_data, lang=to_language, slow=False)
    speech_buffer = BytesIO()
    tts.write_to_fp(speech_buffer)
    speech_buffer.seek(0)
    st.audio(speech_buffer, format="audio/mp3")

# Audio processor for real-time speech recognition
class SpeechRecognizerProcessor(AudioProcessorBase):
    def __init__(self, from_language, to_language):
        self.recognizer = sr.Recognizer()
        self.from_language = from_language
        self.to_language = to_language

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        output_placeholder = st.session_state.output_placeholder

        audio_data = frame.to_ndarray()
        audio = sr.AudioData(audio_data.tobytes(), frame.sample_rate, 2)

        try:
            spoken_text = self.recognizer.recognize_google(audio, language=self.from_language)
            output_placeholder.text(f"🗣️ You said: {spoken_text}")

            translated_text = translator_function(spoken_text, self.from_language, self.to_language)
            output_placeholder.text(f"🔊 Translation: {translated_text}")

            text_to_voice(translated_text, self.to_language)

        except Exception as e:
            pass

        return frame

# UI layout
st.title("🗣️ Real-time Voice Translator (Streamlit Cloud)")

from_language_name = st.selectbox("Select Source Language:", list(LANGUAGES.values()), index=21)
to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()), index=32)

from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

if "output_placeholder" not in st.session_state:
    st.session_state.output_placeholder = st.empty()

if "isTranslateOn" not in st.session_state:
    st.session_state.isTranslateOn = False

if st.button("Start"):
    st.session_state.isTranslateOn = True
    webrtc_streamer(key="speech_translator",
                    mode=WebRtcMode.SENDONLY,
                    audio_processor_factory=lambda: SpeechRecognizerProcessor(from_language, to_language))

if st.button("Stop"):
    st.session_state.isTranslateOn = False
    st.warning("🛑 Translation Stopped.")
