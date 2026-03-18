from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

# Ensure Data folder exists
os.makedirs("Data", exist_ok=True)

# Load or create chat log
chat_log_path = r"Data\ChatLog.json"

try:
    with open(chat_log_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(chat_log_path, "w") as f:
        dump([], f)

# System Prompt
System = f"""
Hello, I am {Username}.
You are a very accurate AI chatbot named {Assistantname}.
Do not tell time unless asked.
Reply only in English.
Do not talk too much.
Do not mention training data.
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Real-time Info Function
def RealtimeInformation():
    now = datetime.datetime.now()

    return f"""
Use this real-time info if needed:
Day: {now.strftime('%A')}
Date: {now.strftime('%d')}
Month: {now.strftime('%B')}
Year: {now.strftime('%Y')}
Time: {now.strftime('%H')}:{now.strftime('%M')}:{now.strftime('%S')}
"""

# Clean formatting
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty = [line for line in lines if line.strip()]
    return "\n".join(non_empty)

# Main Chatbot
def ChatBot(Query):
    try:
        global messages

        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", # UPDATE THE MDDEL LATEST VERSION
            messages=SystemChatBot +
                     [{"role": "system", "content": RealtimeInformation()}] +
                     messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        Answer = ""

        #Concatenate response chunks from the streaming output
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # clean up the response
        Answer = Answer.replace("</s>", "")
        Answer = Answer.replace("**", "")

        messages.append({"role": "assistant", "content": Answer})

        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print("Error:", e)
        return "Something went wrong. Please check API key or model."

# Main entry point of the program for interactive the query Run
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))