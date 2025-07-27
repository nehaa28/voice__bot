🎙️ Voice-Based Interview Agent
================================

A Streamlit web application that conducts an interactive, voice-based interview using:

- 🎤 Real-time audio recording via `streamlit-webrtc`
- 🧠 LLM responses powered by Groq (LLaMA 3)
- 🗣️ Text-to-speech from ElevenLabs
- ✍️ Transcription using OpenAI Whisper

------------------------------------------------------------

🚀 Features
-----------

- 👨‍💼 Asks predefined interview questions using AI-generated speech
- 🎙️ Records user's spoken response in-browser
- 🧾 Transcribes audio to text using OpenAI Whisper
- 💬 Responds with contextual follow-up using LLaMA-3 via Groq API
- 🔁 Repeats until the interview is complete

------------------------------------------------------------

📦 Dependencies
---------------

Install via pip:

```bash
pip install streamlit streamlit-webrtc python-dotenv requests groq elevenlabs av

------------------------------------------------------------

🔐 Environment Variables
------------------------

Create a `.env` file in your project root:

```bash
GROQ_API_KEY=your_groq_api_key  
ELEVEN_API_KEY=your_elevenlabs_api_key  
OPENAI_API_KEY=your_openai_api_key

------------------------------------------------------------

▶️ How to Run
-------------

```bash
streamlit run app.py

Then open your browser at: http://localhost:8501

------------------------------------------------------------

📁 Project Structure
--------------------

.
├── app.py           # Main Streamlit app  
├── .env             # Environment variables (keep secret)  
├── requirements.txt # Optional: dependency list  
└── README.md        # This file

------------------------------------------------------------

🛠️ Tech Stack
--------------

Frontend       : Streamlit  
Audio Stream   : streamlit-webrtc + AV  
LLM            : Groq (LLaMA-3)  
Transcription  : OpenAI Whisper API  
TTS            : ElevenLabs API

------------------------------------------------------------

📌 Notes
--------

- Microphone access is required
- Works best in Chrome or Edge
- You can expand this app with:
  - Custom voice profiles
  - Saving responses to a database
  - Adding evaluation/scoring modules

------------------------------------------------------------

📄 License
----------

MIT License — feel free to modify and share.

------------------------------------------------------------

👏 Credits
---------

Built with ❤️ using Streamlit, Groq, ElevenLabs, and OpenAI.
