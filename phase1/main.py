import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import whisper
from gtts import gTTS
import os
import tempfile
import platform
from transformers import pipeline

# === Audio recording ===
def record_audio(filename="input.wav", duration=5, fs=16000):
    print("🎙️ Speak now...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    scipy.io.wavfile.write(filename, fs, audio)
    print("✅ Recording saved.")

# === Speech to text ===
model = whisper.load_model("base")  # Can change to "tiny" for speed

def transcribe(filename="input.wav"):
    print("📝 Transcribing...")
    result = model.transcribe(filename)
    return result["text"]

# === Text generation ===
interviewer = pipeline("text-generation", model="tiiuae/falcon-rw-1b")

def generate_response(prompt):
    full_prompt = f"### Interviewer: {prompt}\n### Candidate:"
    response = interviewer(full_prompt, max_length=100, do_sample=True)[0]["generated_text"]
    return response.split("### Candidate:")[-1].strip()

# === Text to speech ===
def speak(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang='en')
        tts.save(fp.name)
        path = fp.name
    if platform.system() == "Windows":
        os.system(f'start {path}')
    elif platform.system() == "Darwin":
        os.system(f'afplay {path}')
    else:
        os.system(f'mpg123 {path}')

# === Main loop ===
def main():
    while True:
        record_audio()
        question = transcribe()
        print(f"👤 You: {question}")
        
        response = generate_response(question)
        print(f"🤖 AI: {response}")
        
        speak(response)

        # Optional: Break condition
        if "exit" in question.lower():
            break

if __name__ == "__main__":
    main()
