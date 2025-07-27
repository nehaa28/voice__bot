from dotenv import load_dotenv
import os
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import requests
from gtts import gTTS
import os
import time

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")



# === CONFIG ===
MODEL_NAME = "llama3-8b-8192"  # Try mixtral-8x7b if needed
DURATION = 5  # seconds to record
FILENAME = "recording.wav"

# === RECORD AUDIO ===
def record_audio():
    print("🎙️ Speak now...")
    fs = 44100  # sample rate
    recording = sd.rec(int(DURATION * fs), samplerate=fs, channels=1)
    sd.wait()
    write(FILENAME, fs, recording)
    print("✅ Recording saved.")

# === TRANSCRIBE WITH WHISPER ===
def transcribe():
    print("📝 Transcribing...")
    model = whisper.load_model("base")
    result = model.transcribe(FILENAME)
    print("👤 You: ", result["text"])
    return result["text"]

# === CALL GROQ API ===
def generate_response_with_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful AI interviewer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    res = requests.post(url, headers=headers, json=data)
    response_text = res.json()["choices"][0]["message"]["content"]
    print("🤖 AI:", response_text.strip())
    return response_text

# === TEXT TO SPEECH ===
def speak_text(text):
    tts = gTTS(text=text)
    audio_file = "response.mp3"
    tts.save(audio_file)
    os.system(f"start {audio_file}")  # use 'afplay' on macOS or 'xdg-open' on Linux

# === MAIN LOOP ===
def main():
    while True:
        record_audio()
        question = transcribe()
        response = generate_response_with_groq(question)
        speak_text(response)
        print("###\n")
        time.sleep(1)

if __name__ == "__main__":
    main()
