import openai
import streamlit as st
import speech_recognition as sr
from gtts import gTTS, lang
import os
import tempfile
import base64
import pycountry
openai.api_key = os.getenv("OPENAI_API_KEY")
# Function to translate text using OpenAI's GPT model
def translate_text(text, source_language, target_language):
    client = openai.OpenAI(api_key='openai.api_key')

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"I am a specialized technical translator translating text from {source_language} to {target_language}. I will first understand the context of the conversation and then translate from {source_language} to {target_language}. I will identify technical terms in the source language and provide detailed explanations or definitions of their meanings in {target_language} after translation."},
            {"role": "user", "content": text}
        ]
    )

    return response.choices[0].message.content.strip()

# Function to recognize speech using the microphone
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.success("Recognized text: " + text)
            return text
        except sr.UnknownValueError:
            st.error("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
    return ""

# Function to speak text using gTTS and return the audio file path
def speak_text(text, language):
    if language not in lang.tts_langs():
        st.error(f"Language not supported: {language}")
        return None
    tts = gTTS(text=text, lang=language)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

# Function to convert language name to ISO 639-1 code
def get_language_code(language_name):
    try:
        language = pycountry.languages.lookup(language_name)
        return language.alpha_2
    except LookupError:
        st.error(f"Language not recognized: {language_name}")
        return None

# Function to autoplay audio in Streamlit
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Streamlit UI
st.title("Medical Translator")
st.write("Translate text from one language to another with detailed explanations for technical terms.")

# Input method selection
input_method = st.radio("Select input method:", ("Text", "Voice"))

# Input text and languages
if input_method == "Text":
    text = st.text_area("Enter the text to translate:")
else:
    if st.button("Record"):
        text = recognize_speech()
        st.session_state['recognized_text'] = text
    text = st.session_state.get('recognized_text', '')

source_language = st.text_input("Enter the source language:")
target_language = st.text_input("Enter the target language:")

# Translate button
if st.button("Translate"):
    if text and source_language and target_language:
        source_language_code = get_language_code(source_language)
        target_language_code = get_language_code(target_language)
        
        if source_language_code and target_language_code:
            translation = translate_text(text, source_language_code, target_language_code)
            st.subheader("Translated text:")
            st.write(translation)
            
            # Speak the translated text
            st.subheader("Speaking the translated text:")
            audio_file_path = speak_text(translation, target_language_code)
            if audio_file_path:
                autoplay_audio(audio_file_path)
    else:
        st.error("Please fill in all fields.")


# import openai
# import streamlit as st

# # Function to translate text using OpenAI's GPT model
# def translate_text(text, source_language, target_language):
#     client = openai.OpenAI(api_key='')

#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": f"I am a specialized technical translator translating text from {source_language} to {target_language}. I will first understand the context of the conversation and then translate from {source_language} to {target_language}. I will identify technical terms in the source language and provide detailed explanations or definitions of their meanings in {target_language} after translation."},
#             {"role": "user", "content": text}
#         ]
#     )

#     return response.choices[0].message.content.strip()

# # Streamlit UI
# st.title("Technical Translator")
# st.write("Translate text from one language to another with detailed explanations for technical terms.")

# # Input text and languages
# text = st.text_area("Enter the text to translate:")
# source_language = st.text_input("Enter the source language:")
# target_language = st.text_input("Enter the target language:")

# # Translate button
# if st.button("Translate"):
#     if text and source_language and target_language:
#         translation = translate_text(text, source_language, target_language)
#         st.subheader("Translated text:")
#         st.write(translation)
#     else:
#         st.error("Please fill in all fields.")