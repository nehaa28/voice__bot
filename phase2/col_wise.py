import streamlit as st
import os
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
from gtts import gTTS
import time
import uuid
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Whisper model (base)
whisper_model = whisper.load_model("base")

# Groq LLM setup
client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

# Function to get next response from LLM
def get_llm_response(messages):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content

# Text-to-Speech (TTS)
def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

# Audio Recording
def record_audio(duration=10, fs=44100):
    st.info("Recording... Speak now!")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.wav")
    write(path, fs, audio)
    return path

# Transcribe audio using Whisper
def transcribe_audio(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

# Initialize page and session state
st.set_page_config(page_title="🎙️ Voice-Based Interview Agent", layout="wide")
st.title("🎙️ Voice-Based Interview Agent")

if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {"role": "system", "content": "You are a professional technical interviewer conducting a virtual voice interview. Ask one question at a time and wait for responses."},
        {"role": "assistant", "content": "Hi, welcome to this virtual interview. How are you feeling today?"}
    ]
    st.session_state.phase = "intro"
    st.session_state.last_audio = ""

# Layout columns
col1, col2 = st.columns([2, 3])

# Interviewer side (left)
with col1:
    st.subheader("🧑‍💼 Interviewer")
    for msg in st.session_state.conversation:
        if msg["role"] == "assistant":
            st.markdown(f"**{msg['content']}**")
            temp_audio = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp3")
            text_to_speech(msg["content"], temp_audio)
            with open(temp_audio, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

# Candidate side (right)
with col2:
    st.subheader("🧑 You:")

    if st.session_state.phase in ["intro", "respond"]:
        if st.button("🎤 Start Responding"):
            audio_path = record_audio()
            transcript = transcribe_audio(audio_path)
            st.session_state.conversation.append({"role": "user", "content": transcript})
            st.session_state.phase = "llm_reply"
            st.rerun()

    elif st.session_state.phase == "llm_reply":
        with st.spinner("Interviewer is thinking..."):
            reply = get_llm_response(st.session_state.conversation)
            st.session_state.conversation.append({"role": "assistant", "content": reply})
            st.session_state.phase = "respond"
            st.rerun()

# Restart / End interview controls
st.divider()
c1, c2 = st.columns([1, 4])
with c1:
    if st.button("🔁 Restart Interview"):
        st.session_state.conversation = [
            {"role": "system", "content": "You are a professional technical interviewer conducting a virtual voice interview. Ask one question at a time and wait for responses."},
            {"role": "assistant", "content": "Hi, welcome to this virtual interview. How are you feeling today?"}
        ]
        st.session_state.phase = "intro"
        st.rerun()

with c2:
    if st.button("❌ END Interview"):
        st.success("Interview ended. Thank you!")
