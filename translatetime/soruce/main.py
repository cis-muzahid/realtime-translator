import os
import time
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from googletrans import LANGUAGES, Translator
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

# Initialize translator
translator = Translator()

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

# Translate the spoken text
def translator_function(spoken_text, from_language, to_language):
    return translator.translate(spoken_text, src=from_language, dest=to_language).text

# Generate and play voice output smoothly using gTTS and pydub
def text_to_voice(text_data, to_language):
    # Generate speech
    tts = gTTS(text=text_data, lang=to_language, slow=False)
    
    # Save to memory instead of a file
    speech_buffer = BytesIO()
    tts.write_to_fp(speech_buffer)
    speech_buffer.seek(0)
    
    # Use pydub to play audio smoothly
    audio = AudioSegment.from_file(speech_buffer, format="mp3")
    play(audio)

# Main translation loop
def main_process(output_placeholder, from_language, to_language):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.success("🎤 Listening and Translating... Speak now!")
        
        while st.session_state.isTranslateOn:
            try:
                # Capture audio
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Recognize speech
                spoken_text = recognizer.recognize_google(audio, language=from_language)
                output_placeholder.text(f"🗣️ You said: {spoken_text}")
                
                # Translate and speak immediately
                translated_text = translator_function(spoken_text, from_language, to_language)
                output_placeholder.text(f"🔊 Translation: {translated_text}")
                
                # Speak translated text smoothly
                text_to_voice(translated_text, to_language)

            except Exception as e:
                print("eee")

# UI layout
st.title("🗣️ Real-time Voice Translator with Smooth Output")

# Select languages
from_language_name = st.selectbox("Select Source Language:", list(LANGUAGES.values()))
to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()))

# Convert language names to language codes
from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

# Control buttons
if "isTranslateOn" not in st.session_state:
    st.session_state.isTranslateOn = False

if st.button("Start"):
    st.session_state.isTranslateOn = True
    output_placeholder = st.empty()
    main_process(output_placeholder, from_language, to_language)

if st.button("Stop"):
    st.session_state.isTranslateOn = False
    st.warning("🛑 Translation Stopped.")
