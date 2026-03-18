"""
      Personal AI Assistant
================================
A voice-activated personal assistant that can:
- Listen to voice commands via microphone
- Accept TYPED queries from the GUI chatbox  ← NEW
- Convert speech to text (Google STT)
- Process commands with AI (OpenAI GPT or rule-based fallback)
- Respond via text-to-speech (pyttsx3)
- Open websites, search Google, tell time/date, and more
"""

from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os




env_vars      = dotenv_values(".env")
Username      = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

DefaultMessage = (
    f"{Username}: Hello {Assistantname}, How are you? "
    f"{Assistantname}: Welcome {Username}. I am doing well. How may I help you?"
)

processes  = []
image_path = os.path.abspath(r"Backend\ImageGeneration.py")
Functions  = ["open", "close", "play", "system", "content",
              "google search", "youtube search"]





def ShowDefaultChatIfNoChats():
    with open(r'Data\ChatLog.json', "r", encoding='utf-8') as f:
        if len(f.read()) <= 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f2:
                f2.write("")
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f3:
                f3.write(DefaultMessage)


def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User",      Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
        f.write(AnswerModifier(formatted_chatlog))


def ShowChatOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as f:
        Data = f.read()
    if len(str(Data)) > 0:
        lines  = Data.split("\n")
        result = '\n'.join(lines)
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
            f.write(result)



# NEW — Typed chatbox query helpers


def GetTypedQuery():
    """
    Read a pending typed query from Queries.data.
    Returns the query string if one is waiting, else empty string.
    """
    path = TempDirectoryPath("Queries.data")
    try:
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            query = f.read().strip()
        if query:
            #  Clear the file immediately so we don't process it twice
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
        return query
    except Exception as e:
        print("GetTypedQuery error:", e)
        return ""


def WriteSpokenText(text):
    """
    Write recognised speech text to Spoken.data so the GUI
    chatbox can display it as  '{Username} (mic): <text>'
    """
    try:
        with open(TempDirectoryPath("Spoken.data"), "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print("WriteSpokenText error:", e)



# Startup

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

    # Ensure helper data-files exist so GUI never crashes on first read
    for fname in ("Queries.data", "Spoken.data"):
        path = TempDirectoryPath(fname)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("")

InitialExecution()



# Core processing  (shared by both voice AND typed queries

def ProcessQuery(Query):
    """
    Takes any query string (from mic OR chatbox) and runs the full
    decision / response pipeline.
    """
    if not Query:
        return

    TaskExecution        = False
    ImageExecution       = False
    ImageGenerationQuery = ""

    # Show what the user said  typed in the chat window
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")

    Decision = FirstLayerDMM(Query)
    print(f"\nDecision: {Decision}\n")

    G = any(i for i in Decision if i.startswith("general"))
    R = any(i for i in Decision if i.startswith("realtime"))

    Merged_query = " and ".join(
        ["".join(i.split()[1:]) for i in Decision
         if i.startswith("general") or i.startswith("realtime")]
    )

    # Check for image generation
    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    # Check for automation tasks
    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    # image generation subprocess if needed
    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", 'w') as f:
            f.write(f"{ImageGenerationQuery} , True")
        try:
            p1 = subprocess.Popen(
                ["python", image_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE, shell=False
            )
            processes.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    # Generate the answer
    if G and R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:

            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                Answer = ChatBot(QueryModifier("Okay, Bye!"))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                SetAssistantStatus("Mic Off...")
                os._exit(1)



# Thread 1 — handles BOTH mic voice input AND typed chatbox input


def FirstThread():
    """
    Priority order every loop:
      1. Check for a typed query from the chatbox  → process immediately
      2. If mic is ON → listen for speech, write to Spoken.data, process
      3. If mic is OFF → ensure status label shows 'Mic off'
    """
    while True:

        # ─ Check typed input first (works regardless of mic state) ──
        typed_query = GetTypedQuery()
        if typed_query:
            SetAssistantStatus("Thinking...")
            ProcessQuery(typed_query)
            sleep(0.1)
            continue

        # ── Voice input (only when mic is toggled ON) ──────────
        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            SetAssistantStatus("Listening...")
            voice_query = SpeechRecognition()

            if voice_query:
                #  Write to Spoken.data so GUI shows "You (mic ..."
                WriteSpokenText(voice_query)
                sleep(0.05)   # tiny pause so GUI picks it up
                ProcessQuery(voice_query)

        else:
            # Mic is OFF — keep status label correct
            if GetAssistantStatus() != "Mic off":
                SetAssistantStatus("Mic off")

        sleep(0.1)



# Thread 2 — GUI (must run on main thread via SecondThread)


def SecondThread():
    GraphicalUserInterface()



# Entry point


if __name__ == "__main__":
    t1 = threading.Thread(target=FirstThread, daemon=True)
    t1.start()
    SecondThread()   # GUI must run on the main thread