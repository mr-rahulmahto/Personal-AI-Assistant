from AppOpener import close , open as appopen
from webbrowser import open as webopen
from pywhatkit import search , playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables from the .env files
env_vars =  dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

#Define CSS classes for parsing specific elements in HTML Content.
classes = ["zCubwf" , "hgKElc" , "LTKOO sY7ric" , "Z0LcW" , "gsrt vk_bk FzvWSb YwPhnf" , "pclqee" , "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc" , "O5uR6d LTKOO" ,"vlzY6d" , "webanswers-webanswers_table_webanswers-table" , "dDoNo ikb4Bb gsrt" , "sXLaOe",
           "LWkfKe" , "VQF4g" , "qv3Wpe" , "kno-rdesc" , "SPZz6b"]

#Define a user-agent for making for web request.
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Initialize the  Groq client with the Api key.
client = Groq(api_key=GroqAPIKey)

#Predefined professional responses for user interaction
professional_responses =[
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with."
    "I'm at your service for any additional question or support you may need-don't hesitate to ask."
    
]

#List to store chatbot messages.
messages = []

#system messages to provide context to the chatbot.
SystemChatBot = [{"role": "system" , "content": f"Hello , I am {os.environ['Username']} , You're a content writer .You have to write content like letter"}]

# Function to a perform a Google search
def GoogleSearch(Topic):
    search(Topic) # use pywhatkit's search function to a perform a Google search
    return True # indicate the success

#GoogleSearch("Mahatma Gandhi") #just check the function

# Function to generate content using AI and Save it to a file.
def Content(Topic):
    
    #Nested function to open a file in Notepad
    def OpenNotepad(File):
        default_text_editor ='notepad.exe' #default text editor
        subprocess.Popen([default_text_editor , File]) #open to the file in Notepad
        
    #Nested function to generate content using AI ChatBot
    def ContentWriterAI(prompt):
        messages.append({"role":"user" , "content": f"{prompt}"}) #Add the user's prompt to messages.
        

        # Generate a response using the Groq client.
        completion = client.chat.completions.create (
            model="llama-3.1-8b-instant", # Specfic the AI model.
            messages=SystemChatBot + messages, # Include system instruction  and chat hsitory
            max_tokens=1024, #Limit the maximum tokens in the responses 
            temperature=0.7, # Adust rsponses randomness.
            top_p=1, # Use  nucleus sampling for responses diversity.
            stream=True, #Enable streaming resposnse.
            stop=None #Allow the model to detrmine stopping condition
        
          )
        
        Answer = ""
        
        #process streamed response chunks.
        for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content
    
        # clean up the response
        Answer = Answer.replace("</s>", "") #Remove unwanted tokens from the response.

        messages.append({"role": "assistant", "content": Answer}) #Add the AI's response to messages.
        
        return Answer
    
    
    Topic: str = Topic.replace("Content" , "") #Remove "Content" fro the topic
    ContentByAI = ContentWriterAI(Topic) #Generate content using AI
    
    #Save the generate content to a text file
    with open (rf"Data\{Topic.lower().replace(' ','')}.txt" , "w" ,encoding="utf-8") as file:
        file.write(ContentByAI) #write the content to the file.
        file.close()
        
    OpenNotepad(rf"Data\{Topic.lower().replace(' ','')}.txt") # Open the file in Notepad
    return True

# Content("application for a sick leave ") #Just check Working Ai model or code
# Function to serach for a topic on YouTube.
def YouTubeSearch(Topic):
    url = f"https://www.youtube.com/results?search_query={Topic}" #construct the youtube search
    webbrowser.open(url)
    return True
#YouTubeSearch("Hanuman chalisha") # its working

# Function to play video on YouTube.
def PlayYouTube(query):
    playonyt(query) # use pywhatkit's playonyt function to play video
    return True

#PlayYouTube("Hanuman chalisha") # its working


#Function  to open an application or a relevant WebPages
def OpenApp(app , sess=requests.session()):
    
    try:
        appopen(app , match_closest=True , output=True , throw_error=True) #Attempt to open the app.
        return True
    except:
        #Nested function to extract link from HTML content.
        def extract_links(html):
            if html is None:
                return[]
            soup = BeautifulSoup(html , 'html.parser') #parser the Html Content
            links = soup.find_all('a') #find relevant link
            return [link.get('href') for link in links if link.get('href') and link.get('href').startswith("http")] #Return the links.
        
        #Nested Function to perform a Google Search and  retrieve HTML
        def search_google(app):
            #check if application is not found desktop then it search webbrowser
            try:
                appopen(app, match_closest=True, output=True, throw_error=True)
                return True
            except:
                url = f"https://www.{app}.com"
                webbrowser.open(url)
                return True
        
        html = search_google(app) #Perform the Google search
        
        if html:
            link = extract_links(html)[0] #Extract the first link from search results.
            webopen(link) #open the link in a web
            
        return True
    

#OpenApp("instagram") #its open webbrowser bcz instagram not present application in system
#OpenApp("Excel") #its open Excel in this system
# Function to close an application
def CloseApp(app):
    
    if "chrome" in app:
        pass #skip if the app in Chrome bcz chrome use speech to Text or speech Recogination Don't closed chrome
    else:
        try:
            close(app , match_closest=True , output=True , throw_error=True) #Attempt to close App
            return True #Indicate Success.
        except:
            return False #indicate failur.
        
#CloseApp("Notepad") #its working
  
#Function to execute system-level commands      
def System(command):
    
    #Nested funcion to mute the system volume.
    def mute():
        keyboard.press_and_release("volume mute") # Simulate the mute key press.
        
    #Nested Function to unmute the system volume
    def unmute():
        keyboard.press_and_release("volume mute") # Simulate the unmute key press.
    
    #Nested Function to increase the system volume
    def volume_up():
        keyboard.press_and_release("volume up") # Simulate the Volume up key press.
        
    #Nested Function to decrease the system volume
    def volume_down():
        keyboard.press_and_release("volume down") # Simulate the Volume down key press.
        
    if command == "mute":
        mute()
    elif command =="unmute":
        unmute()
    elif command =="volume_up":
        volume_up()
    elif command == "volume_down":
        volume_down()
    return True

#System("unmute") its working

#Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands:list[str]):
    
    funcs = [] #List to store asynchronous Task
    
    for command in commands:
        
        if command.startswith("open "): #Handle "open" Commands.
            
            if "open it" in command: #ignore "open it" Commands.
                pass
            if "open file" == command: #ignore "open file" commands.
                pass
            
            else:
                fun = asyncio.to_thread(OpenApp , command.removeprefix("open ")) #schedule app opening.
                funcs.append(fun)
                
        elif command.startswith("general "): #Placeholder for general commands
            pass
        
        elif command.startswith("realtime "): #Placeholder for Realtime commands.
            pass
        
        elif command.startswith("close "): #Handle "close" Commands.
            fun = asyncio.to_thread(CloseApp , command.removeprefix("close ")) #schedule app closing.
            funcs.append(fun)
            
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYouTube , command.removeprefix("play "))
            funcs.append(fun)
            
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content , command.removeprefix("content "))
            funcs.append(fun)
            
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch , command.removeprefix("google search "))
            funcs.append(fun)
            
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch , command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System , command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"No Function found . for {command}")
            
    results = await asyncio.gather(*funcs) #Execute all tasks concurrently.
    
    for result in results : #Process the results.
        if isinstance(result , str):
            yield result
        else:
            yield result
            
#Asynchronous function to  automate command execution.

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands): #Translate and excute commands.
        pass
    return True


#Mutliple Application run at time    
if __name__ == "__main__":

     
    asyncio.run(Automation(["open whatsapp" , "open facebook" , "open Notepad" , "play song", "content song for me"]))
         