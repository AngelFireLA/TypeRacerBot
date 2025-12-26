import io
import os
import random
import time

import mss
from PIL import Image
from pynput.keyboard import Controller
from playwright.sync_api import sync_playwright
from pynput import keyboard
import keyboard
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini with your API key
GENAI_API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=GENAI_API_KEY)
system_instruction = "You will be given an image, answer the text in the image as accurately as possible. Don't say anything else, no formatting, just repeat the text exactly. The only thing you don't need to do is change line. Always answer as if the text was one line. Be careful of spaces, punctuation, accentuation, that needs to eb the exact same as in the image."

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    thinking_config=types.ThinkingConfig(thinking_level="minimal")
)

def generate_response(model_name="models/gemini-3-flash-preview"):


    with mss.mss() as sct:
        region = {
            "left": 443,
            "top": 315,
            "width": 406,
            "height": 128
        }

        sct_img = sct.grab(region)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        # save image to file for debugging
        img.save("screenshot_debug.jpg")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')

    img_bytes = img_byte_arr.getvalue()

    image_data = types.Part.from_bytes(
            data=img_bytes,
            mime_type='image/jpeg',
        )
    response = client.models.generate_content(
        model=model_name,
        config=config,
        contents=[image_data],
    )
    print("reponse received", response.text)
    return response.text


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)

        page = browser.new_page()

        url = "https://play.typeracer.com/"

        page.goto(url)
        kb = Controller()
        while True:
            keyboard.wait('f9')
            target_locator = page.locator('div[style*="font-family: monospace"]')
            full_string = target_locator.inner_text()

            print("Extracted Text :")
            print(full_string)

            a, b = 30, 60
            keyboard.wait('f9')
            for letter in full_string:
                time.sleep(random.randint(a, b)/1000)
                kb.type(letter)
            keyboard.wait('f9')

            more_text_to_write = generate_response()
            print(more_text_to_write)
            for letter in more_text_to_write:
                time.sleep(random.randint(a//3, b//3)/1000)
                kb.type(letter)

run()