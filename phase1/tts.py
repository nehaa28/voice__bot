# from TTS.api import TTS

# tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

# def speak(text, filename="response.wav"):
#     tts.tts_to_file(text=text, file_path=filename)

from gtts import gTTS
import os
import tempfile
import platform

def speak(text):
    # Save to a temporary MP3 file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang='en')
        tts.save(fp.name)
        path = fp.name

    # Play it depending on OS
    if platform.system() == "Windows":
        os.system(f'start {path}')
    elif platform.system() == "Darwin":
        os.system(f'afplay {path}')
    else:
        os.system(f'mpg123 {path}')

