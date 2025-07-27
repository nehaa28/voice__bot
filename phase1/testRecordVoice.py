import sounddevice as sd
import numpy as np

duration = 3  # seconds
fs = 16000

print("Recording...")
audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
sd.wait()
print("Done!")

# Save if you want to verify it recorded
import scipy.io.wavfile
scipy.io.wavfile.write("test.wav", fs, audio)
