# 💀 DOOM — AI Voice Assistant

> *"I am DOOM — your most dangerous friend and most loyal assistant."*

A locally-running, multi-modal AI voice assistant built on Python — combining Face Recognition, Large Language Models, Real-time Speech Processing, and a dark sarcastic personality into one system that serves only its master.

---

## ⚡ Demo

```
> wake up doom
[DOOM]: Checking identity...
[FACE VERIFIED]: Welcome, Divyansh.
[DOOM]: "Not as useless as you. Tell me what you need."
```

---

## 🧠 Architecture

```
Speech Input (Mic)
      ↓
Wake Word Detection
      ↓
Face Verification (CV2 + face_recognition)
      ↓
Command Parser (Rule-based NLP)
      ↓  ↘
Built-in        LLM Fallback
Commands        (Groq API — llama-3.3-70b)
      ↓  ↙
Conversation Memory (Buffer)
      ↓
TTS Output (pyttsx3 — Zarvox voice)
```

---

## 🚀 Features

### Phase 1 — Voice Engine ✅
- Speech-to-text via Google Speech API (`speech_recognition`)
- Text-to-speech via `pyttsx3` — Zarvox voice (Mac built-in), 150 WPM
- Multi-variation wake word detection: `"wake up doom"`, `"hey doom"`, `"activate doom"` etc.

### Phase 2 — Command System ✅
- **Time & Date** — `datetime` module
- **Wikipedia Search** — query extraction + `wikipedia` library
- **Google Search** — `webbrowser` + URL construction
- **App Launcher** — `os.system("open -a 'AppName'")` — dictionary-based
- **Website Opener** — `webbrowser.open()` — dictionary-based
- **LLM Fallback** — any unrecognized command → Groq API handles it

### Phase 3 — Face Unlock ✅
- `face_recognition` (dlib) + `OpenCV` — 128-point facial encoding
- Reference photo comparison using Euclidean distance threshold
- 3 failed speech attempts → automatic face re-scan
- Unknown face detected → `sys.exit()` (Access Denied)

### Phase 4 — LLM Brain ✅
- **Provider:** Groq API (free tier — 14,400 requests/day)
- **Model:** `llama-3.3-70b-versatile` — Meta's open-source LLM
- **Why Groq:** Custom LPU (Language Processing Unit) chip — ~10x faster than GPU inference
- **Personality:** Dark, sarcastic, Hinglish — never breaks character

### Phase 5 — Conversation Memory ✅
- **Type:** Short-term Buffer Memory
- Maintains full `conversation_history` list across the session
- Each Groq API call receives: `[system_prompt] + full_history`
- LLM is stateless by design — memory is an architectural trick, not model state

---

## 🔐 Security Loop

```
OUTER LOOP → Wake word listening (always on)
    ↓ Wake word detected
    verify_face() → webcam scan → encoding match
    ↓ Identity confirmed
INNER LOOP → Command processing
    ↓ "goodnight" → sleep mode (back to outer loop)
    ↓ "exit"      → sys.exit() (full shutdown)
    ↓ 3x unknown  → re-verify face
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Speech Recognition | `speech_recognition` + Google Speech API |
| Text-to-Speech | `pyttsx3` — Zarvox voice |
| Face Recognition | `face_recognition` (dlib) + `opencv-python` |
| LLM | Groq API — `llama-3.3-70b-versatile` |
| Memory | Custom buffer — `conversation_history` list |
| Commands | Rule-based `if/elif` + `datetime`, `wikipedia`, `webbrowser`, `os` |
| Environment | `python-dotenv` — `.env` key management |

---

## 📁 File Structure

```
DOOM/
├── Doom.py            ← Main brain
├── divyansh.jpeg      ← Reference face (gitignored)
├── .env               ← API keys (gitignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone https://github.com/DivyTiwari-ship-it/DOOM.git
cd DOOM
pip install -r requirements.txt
```

### 2. Requirements

```txt
speechrecognition
pyttsx3
face_recognition
opencv-python
groq
wikipedia
python-dotenv
```

### 3. Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Reference Photo

Add your face photo as `divyansh.jpeg` in the project root.

### 5. Run

```bash
python3 Doom.py
```

---

## 💬 Personality

DOOM is not your average assistant. It is dark, sarcastic, and brutally loyal.

- Raw humor — roasts when needed, loyal when it matters
- Short 1-2 line replies — optimized for voice
- Responds in Hinglish (Hindi + English mix) by default
- Never breaks character. Ever.

---

## 🗺️ Roadmap

- [x] Voice Engine (STT + TTS)
- [x] Wake Word Detection
- [x] Face Unlock Security
- [x] LLM Integration (Groq — llama-3.3-70b)
- [x] Short-term Conversation Memory
- [ ] JARVIS-style Web GUI (WebSocket)
- [ ] YOLOv8 Person Detection — "Someone is behind you, master"
- [ ] Emotion Detection CNN — mood-aware responses
- [ ] RAG + Vector DB (ChromaDB) — permanent project memory
- [ ] Public Web Deployment — shareable URL
- [ ] IEEE Research Paper (Overleaf/LaTeX)

---

## 🔬 Technical Concepts

**How does face recognition work?**
dlib's deep learning model detects 128 facial landmarks and generates a 128-dimensional encoding vector. To compare two faces, Euclidean distance is calculated between their encodings — below 0.6 threshold means same person.

**How was memory added to the LLM?**
LLMs are stateless — every API call is independent with no built-in memory. The trick is to send the full `conversation_history` list with every request. The model sees it as one continuous conversation.

**Why Groq instead of standard GPU inference?**
Groq uses a custom LPU (Language Processing Unit) chip specifically designed for LLM inference — delivering approximately 10x faster response times compared to GPU-based inference for the same model.

**What is a system prompt?**
A system prompt provides the LLM with initial instructions, personality, and constraints. It is sent at the start of every conversation as a `role: system` message and defines how the model behaves throughout the session.

---

## 👤 Author

**Divyansh Tiwari**
BCA Final Year | ML/AI Developer

- GitHub: [@DivyTiwari-ship-it](https://github.com/DivyTiwari-ship-it)
- Portfolio: [divytiwari-ship-it.github.io](https://divytiwari-ship-it.github.io/divyanshtiwari.github.io)
- Kaggle: [kaggle.com/divyanshtiwari01](https://kaggle.com/divyanshtiwari01)

---

> *Built at 2AM. Powered by Groq. Secured by face. Loyal to one master.*
