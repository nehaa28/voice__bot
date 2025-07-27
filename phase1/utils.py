
import sounddevice as sd
import numpy as np
import scipy.io.wavfile

def record_audio(filename="input.wav", duration=5, samplerate=16000):
    print("🎤 Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    scipy.io.wavfile.write(filename, samplerate, audio)
    print("✅ Recording complete")

def play_audio(filename="response.wav"):
    import wave
    import pyaudio

    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)
    stream.stop_stream()
    stream.close()
    p.terminate()
