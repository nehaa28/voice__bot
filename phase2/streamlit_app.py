import os
import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
from gtts import gTTS
import tempfile
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Voice Interview Bot", layout="centered")
st.title("🎤 Voice Interview Agent")

DURATION = 5  # seconds
SAMPLE_RATE = 44100
MODEL_NAME = "llama3-8b-8192"

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()

def record_voice():
    st.info("Recording for 5 seconds... 🎙️")
    audio = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    write(temp_audio_path, SAMPLE_RATE, audio)
    return temp_audio_path

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]

def generate_groq_response(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def speak_text(text):
    tts = gTTS(text)
    tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    tts.save(tts_file)
    return tts_file

if st.button("🎙️ Start Interview"):
    audio_path = record_voice()
    st.success("✅ Recorded")
    
    st.write("📝 Transcribing...")
    question = transcribe_audio(audio_path)
    st.text_area("👤 You Asked:", question, height=100)

    if question.strip():
        st.write("🤖 Generating AI Response...")
        try:
            answer = generate_groq_response(question)
            st.text_area("🤖 AI Answer:", answer, height=150)

            st.write("🔊 Speaking Response...")
            tts_file = speak_text(answer)
            st.audio(tts_file, format="audio/mp3")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("No speech detected.")
