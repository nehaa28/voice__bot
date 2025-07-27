import streamlit as st
from dotenv import load_dotenv
import os
import base64
import uuid
import tempfile
import requests
import queue
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from groq import Groq
from elevenlabs import ElevenLabs

# Page setup
st.set_page_config(page_title="Voice-Based Interview Agent", layout="wide")

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize clients
groq_client = Groq(api_key=GROQ_API_KEY)
eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY)

# App title
st.markdown("<h1 style='font-size: 3em;'>🎙️ Voice-Based Interview Agent</h1>", unsafe_allow_html=True)

# Session state init
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "waiting_for_user" not in st.session_state:
    st.session_state.waiting_for_user = False

# Predefined questions
questions = [
    "Hi, welcome to this virtual interview. How are you feeling today?",
    "Let's get started then. Can you tell me about a project you worked on that you're particularly proud of, and what your role was in that project?",
    "That sounds interesting! As a lead data scientist, can you walk me through the problem you were trying to solve in that project, and how you approached it from a technical standpoint?",
]

# Text-to-speech using ElevenLabs
def text_to_speech(text, filename):
    audio = eleven_client.text_to_speech.convert(
        voice_id="9BWtsMINqrJLrRacOk9x",
        model_id="eleven_monolingual_v1",
        text=text
    )
    with open(filename, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return filename

# Transcription via OpenAI Whisper
@st.cache_data(show_spinner=False)
def transcribe(audio_path):
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    response = requests.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        files={"file": (audio_path, audio_data)},
        data={"model": "whisper-1"},
    )
    return response.json()["text"]

# LLM completion
def interview_response():
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
    chat_completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
    )
    return chat_completion.choices[0].message.content

# Display chat history
for msg in st.session_state.chat_history:
    col1, col2 = st.columns([1, 6])
    if msg["role"] == "assistant":
        with col1:
            st.markdown("👨‍💼 **Interviewer**")
        with col2:
            st.write(msg["content"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/wav")
    elif msg["role"] == "user":
        with col1:
            st.markdown("🧑‍💻 **You**")
        with col2:
            st.write(msg["content"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/wav")

# Ask next question (only if not waiting on response)
if st.session_state.current_question < len(questions) and not st.session_state.waiting_for_user:
    question = questions[st.session_state.current_question]
    filename = f"interviewer_q{st.session_state.current_question}.wav"
    text_to_speech(question, filename)
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": question,
        "audio": filename
    })
    st.session_state.waiting_for_user = True

# Audio recording setup
st.markdown("#### 🎤 Ready to respond?")
audio_queue = queue.Queue()

def audio_callback(frame: av.AudioFrame):
    sound = frame.to_ndarray()
    return av.AudioFrame.from_ndarray(sound, layout="mono")

webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    audio_frame_callback=audio_callback,
)

# Submit button to handle response
if st.button("Submit Response"):
    if not audio_queue.empty():
        raw_audio = b"".join([frame.tobytes() for frame in list(audio_queue.queue)])
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(raw_audio)
            user_audio_path = tmp_file.name

        user_text = transcribe(user_audio_path)
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_text,
            "audio": user_audio_path
        })

        # Interviewer response
        reply = interview_response()
        filename = f"interviewer_q{st.session_state.current_question}_reply.wav"
        text_to_speech(reply, filename)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": reply,
            "audio": filename
        })

        # Move to next question
        st.session_state.current_question += 1
        st.session_state.waiting_for_user = False

# End of interview
if st.session_state.current_question >= len(questions):
    st.success("✅ The interview has concluded. Thank you!")
