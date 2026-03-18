# 🤖 Personal AI Assistant

> A voice-activated, AI-powered personal assistant with a sleek PyQt5 GUI — capable of listening to your voice, understanding natural language, searching the web in real time, automating tasks, and responding with text-to-speech.

---

## ✨ Features

- 🎙️ **Voice Recognition** — Speak to the assistant using your microphone
- ⌨️ **Typed Input** — Type queries directly in the chat box
- 🧠 **AI Brain** — Powered by Groq & Cohere LLMs for fast, intelligent responses
- 🔍 **Real-time Web Search** — Searches the web for up-to-date answers
- 🖼️ **Image Generation** — Generate images from text prompts
- 🔊 **Text-to-Speech** — Responds back with a natural voice (Edge TTS)
- 🖥️ **Automation** — Opens apps, plays music, searches YouTube/Google, and more
- 💬 **Chat History** — Full conversation log with a beautiful dark UI

---

## 🗂️ Project Structure

```
📦 Root
├── main.py                  # Entry point
├── Requirements.txt         # All dependencies
├── .env                     # API keys & config (YOU create this)
├── .gitignore
│
├── 📁 Frontend
│   ├── GUI.py               # PyQt5 interface
│   ├── 📁 Graphics          # Icons, GIFs, images
│   └── 📁 Files             # Runtime data files (YOU create these)
│       ├── Responses.data
│       ├── Database.data
│       ├── ImageGeneration.data
│       ├── Status.data
│       ├── Mic.data
│       ├── Queries.data
│       └── Spoken.data
│
├── 📁 Backend
│   ├── Model.py             # First layer decision model
│   ├── Chatbot.py           # LLM chatbot logic
│   ├── RealtimeSearchEngine.py
│   ├── SpeechToText.py
│   ├── TextToSpeech.py
│   ├── Automation.py
│   └── ImageGeneration.py
│
└── 📁 Data                  # Chat logs (YOU create this folder)
    └── ChatLog.json
```

---

## ⚙️ Setup Guide

Follow every step carefully in order.

---

### ✅ Step 1 — Create Python Virtual Environment

> **Requires Python 3.10.7** — [Download here](https://www.python.org/downloads/release/python-3107/)

Open your terminal in the **project root folder** and run **one** of these:

```bash
# Option A — if you have multiple Python versions installed
py -3.10 -m venv envjarvis

# Option B — if Python 3.10 is your default
pip -m venv envjarvis
```

Then **activate** the environment in VS Code terminal:

```bash
envjarvis\Scripts\activate
```

> ✅ You should see `(envjarvis)` at the start of your terminal prompt.

---

### ✅ Step 2 — Install Required Packages

Make sure your `envjarvis` environment is active, then run:

```bash
pip install -r Requirements.txt
```

**`Requirements.txt` contents:**

```
python-dotenv
groq
AppOpener
pywhatkit
bs4
pillow
rich
requests
keyboard
cohere
googlesearch-python==1.2.3
selenium
mtranslate
pygame
edge-tts
PyQt5
ddgs
fal_client
pyperclip
webdriver-manager
```

> ⏳ This may take a few minutes — all packages will install automatically.

---

### ✅ Step 3 — Create the `Data` Folder

In the **root directory** of the project, create a folder named exactly:

```
Data
```

Inside it, create an empty file:

```
Data/
└── ChatLog.json
```

Paste this content into `ChatLog.json`:

```json
[]
```

> This file stores your conversation history.

---

### ✅ Step 4 — Create Runtime Data Files

Inside the `Frontend` folder, create a subfolder named `Files`:

```
Frontend/
└── Files/
```

Then create these **7 empty files** inside `Frontend/Files/`:

| File | Purpose |
|---|---|
| `Responses.data` | Stores AI responses for the GUI |
| `Database.data` | Stores formatted chat history |
| `ImageGeneration.data` | Stores image generation requests |
| `Status.data` | Stores assistant status text |
| `Mic.data` | Stores microphone on/off state |
| `Queries.data` | Stores typed chat queries |
| `Spoken.data` | Stores recognised speech text |

You can create them all at once using this command in your terminal:

```bash
# Windows (PowerShell)
cd Frontend\Files
New-Item Responses.data, Database.data, ImageGeneration.data, Status.data, Mic.data, Queries.data, Spoken.data
```

---

### ✅ Step 5 — Configure Your `.env` File

Create a `.env` file in the **root directory** and fill in your details:

```env
# Your name
Username=YourName

# Assistant name
Assistantname=Jarvis

# API Keys
GROQ_API_KEY=your_groq_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
FAL_KEY=your_fal_ai_key_here
```

> 🔑 Get your API keys from:
> - Groq → [console.groq.com](https://console.groq.com)
> - Cohere → [dashboard.cohere.com](https://dashboard.cohere.com)
> - Fal AI → [fal.ai](https://fal.ai)
> - HuggingFace -> [ImageGenerationAPI(https://huggingface.co/spaces?category=code-generation)]

---

### ✅ Step 6 — Run the Assistant

Make sure your `envjarvis` environment is **active**, then run:

```bash
python main.py
```

> 🎉 The GUI will launch. Click the **mic button** to start speaking or type in the chat box!

---

## 🎮 How to Use

| Action | How |
|---|---|
| 🎙️ Voice input | Click the **mic button** to toggle listening ON/OFF |
| ⌨️ Typed input | Type in the chat box and press **Enter** or click **➤** |
| 🏠 Home screen | Click **Home** in the top bar |
| 💬 Chat screen | Click **Chats** in the top bar |
| ➖ Minimize | Click the minimize button in the top bar |
| ⬜ Maximize | Click the maximize button in the top bar |
| ✖️ Close | Click the close button in the top bar |

---

## 💬 Example Commands

```
"Open YouTube"
"Search Google for Python tutorials"
"What's the weather today?"
"Play Believer on YouTube"
"Generate an image of a futuristic city"
"What time is it?"
"Tell me a joke"
"Who is Elon Musk?"
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Make sure `envjarvis` is active and run `pip install -r Requirements.txt` |
| Mic not working | Check microphone permissions in Windows Settings |
| GUI doesn't open | Make sure PyQt5 installed correctly: `pip install PyQt5` |
| `.env` not found | Make sure `.env` is in the **root folder**, not inside a subfolder |
| `ChatLog.json` error | Make sure `Data/ChatLog.json` exists and contains `[]` |
| `FileNotFoundError` on `.data` files | Create all 7 files in `Frontend/Files/` (see Step 4) |

---

## 📦 Tech Stack

| Component | Technology |
|---|---|
| GUI | PyQt5 |
| Voice Recognition | Google Speech-to-Text (via SpeechRecognition) |
| Text-to-Speech | Microsoft Edge TTS |
| AI / LLM | Groq (LLaMA), Cohere |
| Web Search | DuckDuckGo Search, Google Search |
| Image Generation | Fal AI |
| Automation | AppOpener, PyWhatKit, Selenium |

---

## 📄 License

This project is for personal and educational use.

---

## 🙌 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## ENV Fie
```env
-InputLanguage= en #also replace hindi (hi)
-AssistantVoice=en-CA-LiamNeural (Also Change voice of Assistant Go through Python Official website)
-CohereAPIKey= API Key Here
-Username = Its your Name
=Assistantname = Personal AI Assistant Name
-GroqAPIKey = API Key Here
-HuggingFaceAPIKey = API key Here
```
<p align="center">Made with ❤️ using Python & PyQt5</p>
