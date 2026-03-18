import asyncio  # Used for asynchronous (non-blocking) programming
from random import randint   # Generates random numbers (used for seed)
from PIL import Image  # Used to open and display images
import requests  # Used to send HTTP requests to HuggingFace API
from dotenv import get_key  # Used to read API key from .env file
import os   # Used for file and folder operations
from time import sleep  # Used to pause execution

# ================== CONFIG ==================
#API details for the Hugging face stable diffusion model
invoke_url = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev"
HF_TOKEN = get_key(".env", "NvidiaAPIKey")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
     
}

# ================== OPEN IMAGES ==================
#Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")

     #Generate the filenames for the images
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for file in files:
        image_path = os.path.join(folder_path, file)

        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)

        #Pause for 1 second befor showing the next image

        except IOError:
            print(f"Unable to open {image_path}")

# ================== API QUERY ==================
#Async function to send a query to the Hugging Face API
async def query(payload):
    response = await asyncio.to_thread(
        requests.post,
        invoke_url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        print("API Error:", response.json())
        return None

    return response.content

# ================== GENERATE IMAGES ==================
# Async function to generate images based on the given prompt
async def generate_images(prompt: str):
    tasks = []


    #Create 4 image generation tasks
    for _ in range(4):
        payload = {
        "prompt":  f"{prompt}",

        # "options": {"wait_for_model": True},
        # "parameters": {"seed": randint(0, 1000000)},
        "mode": "base",
        "cfg_scale": 3.5,
        "width": 1024,
        "height": 1024,
        "seed": 0,
        "steps": 50
        }

        tasks.append(asyncio.create_task(query(payload)))
    #Wait for all tasks to complete
    results = await asyncio.gather(*tasks)

    os.makedirs("Data", exist_ok=True)

    # Save the generate images to files
    for i, image_bytes in enumerate(results):
        if image_bytes:
            with open(f"Data/{prompt.replace(' ', '_')}{i+1}.jpg", "wb") as f:
                f.write(image_bytes)

# ================== WRAPPER ==================
# wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# ================== MAIN LOOP ==================
#Main loop to monitor for  image generation request
while True:
    try:
        with open("Frontend/Files/ImageGeneration.data", "r") as f:
            data = f.read().strip()

        # if "," not in data:
        #     sleep(1)
        #     continue

        Prompt, Status = [x.strip() for x in data.split(",")]

         #If the status indiCates an images generation request
        if Status == "True":
            print("Generating Images...")
            GenerateImages(Prompt)

             #Reset the status in the files afterr generating images
            with open("Frontend/Files/ImageGeneration.data", "w") as f:
                f.write("False, False")

        sleep(1) #WAIT for 1 second before checking again

    except Exception as e:
        print("Error:", e)
        sleep(2)