from stt import transcribe
from llm import generate_response
from tts import speak
from utils import record_audio, play_audio

if __name__ == "__main__":
    print("🤖 Interview Bot Initialized!")
    while True:
        record_audio()
        user_input = transcribe("input.wav")
        print(f"👤 You: {user_input}")

        if any(x in user_input.lower() for x in ["exit", "quit", "stop"]):
            print("👋 Goodbye!")
            break

        response = generate_response(user_input)
        print(f"🤖 Bot: {response}")
        speak(response)
        play_audio("response.wav")
