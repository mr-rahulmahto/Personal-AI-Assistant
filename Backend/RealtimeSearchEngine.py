from googlesearch import search
from ddgs import DDGS
from groq import Groq
from json import load , dump
import datetime
from dotenv import dotenv_values
import os


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

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""


#Function to perform a Google search and format the results.

def GoogleSearch(query):
    Answer = f"The search results for '{query}' are:\n[start]\n"

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

            if not results:
                Answer += "No results found.\n"

            for r in results:
                Answer += f"Title: {r.get('title')}\n"
                Answer += f"Description: {r.get('body')[:200]}\n"
                # Answer += f"URL: {r.get('href')}\n\n"

    except Exception as e:
        Answer += f"Error occurred: {e}\n"

    Answer += "[end]"
    # print(Answer)
    return Answer

#Function to Clean up the answer by removing empty lines.
# Clean formatting
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty = [line for line in lines if line.strip()]
    return "\n".join(non_empty)


#Predefined Chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system" , "content": System },
    {"role": "user" , "content": "Hi"},
    {"role": "assistant" , "content": "Hello , how can I help you ?"}
]

# Function to get real-time information like the current date and time
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
# Function to handle real-time search and response generation
def RealtimeSearchEngine(prompt):
    try:

        global SystemChatBot , messages

        #Load the chat log from the json file.
        with open(chat_log_path, "r") as f:
            messages = load(f)[-5:]
        messages.append({"role": "user" , "content": f"{prompt}"})

        #Add Google Search Result to the system chatbot message.
        # SystemChatBot.append({"role": "system" , "content": GoogleSearch(prompt)})

        search_data = GoogleSearch(prompt)
        realtime_data = RealtimeInformation()

        # Generate a response using the Groq client.
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", # UPDATE THE MDDEL LATEST VERSION #openai/gpt-oss-120b
            messages=SystemChatBot +[ 
                    {"role": "system", "content": System},
                    {"role": "system", "content": realtime_data},
                    {"role": "system", "content": search_data}
                ] + messages,
                    
            max_tokens=300,
            temperature=0.7,
            top_p=1,
            stream=True
        
        )

        Answer = ""

        for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content
    
        # clean up the response
        Answer = Answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": Answer})


        # Save the update chat log back to the Json file
        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        #Remove the most recent system message from the chatbot conversation
        SystemChatBot.pop()
        return AnswerModifier(Answer)

    except Exception as e:
        print("Error:", e)
        return "Something went wrong. Please check API key or model."

# Main entry point of the program for interactive the query Run
if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query: ")
        print(RealtimeSearchEngine(prompt))



