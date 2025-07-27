import whisper

model = whisper.load_model("base")  # or "small", "medium"

def transcribe(audio_path):
    result = model.transcribe(audio_path)
    return result['text']
