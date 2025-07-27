import streamlit as st
import os
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
from gtts import gTTS
import time
from transformers import pipeline
from dotenv import load_dotenv
import openai
import uuid
from openai import OpenAI

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Load Whisper model
whisper_model = whisper.load_model("base")

# Groq client setup
openai.api_key = GROQ_API_KEY
openai.api_base = "https://api.groq.com/openai/v1"

# Initialize LLM
client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

def get_llm_response(messages):
    response = client.chat.completions.create(
        model="llama3-70b-8192",  # ✅ New supported model
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content

# TTS generation
def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

# Record audio
def record_audio(duration=5, fs=44100):
    st.info("Recording... Speak now!")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    temp_audio_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.wav")
    write(temp_audio_path, fs, audio)
    return temp_audio_path

# Transcription
def transcribe_audio(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

# App UI
st.set_page_config(page_title="AI Interviewer", layout="centered")
st.title("🎙️ Voice-Based Interview Agent")

# Session state
if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {"role": "system", "content": "You are a professional technical interviewer conducting a virtual voice interview. Ask one question at a time and wait for responses."},
        {"role": "assistant", "content": "Hi, welcome to this virtual interview. How are you feeling today?"}
    ]
    st.session_state.phase = "play_intro"
    st.session_state.audio_ready = False

st.divider()

# Play voice message
if st.session_state.phase == "play_intro":
    first_question = st.session_state.conversation[-1]["content"]
    st.markdown(f"👨‍💼 **Interviewer:** {first_question}")
    intro_audio_path = os.path.join(tempfile.gettempdir(), "intro.mp3")
    text_to_speech(first_question, intro_audio_path)
    with open(intro_audio_path, "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3")
    st.session_state.phase = "wait_response"

# Record candidate response
if st.session_state.phase == "wait_response":
    if st.button("🎤 Respond Now"):
        audio_path = record_audio()
        transcript = transcribe_audio(audio_path)
        st.markdown(f"🧑 **You:** {transcript}")
        st.session_state.conversation.append({"role": "user", "content": transcript})
        st.session_state.phase = "ask_next"

# Generate next question
if st.session_state.phase == "ask_next":
    with st.spinner("Thinking..."):
        next_question = get_llm_response(st.session_state.conversation)
        st.session_state.conversation.append({"role": "assistant", "content": next_question})
        next_audio_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp3")
        text_to_speech(next_question, next_audio_path)
        st.markdown(f"👨‍💼 **Interviewer:** {next_question}")
        with open(next_audio_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")
    st.session_state.phase = "wait_response"

# Option to restart
if st.button("🔁 Restart Interview"):
    st.session_state.conversation = [
        {"role": "system", "content": "You are a professional technical interviewer conducting a virtual voice interview. Ask one question at a time and wait for responses."},
        {"role": "assistant", "content": "Hi, welcome to this virtual interview. How are you feeling today?"}
    ]
    st.session_state.phase = "play_intro"
    st.rerun()

