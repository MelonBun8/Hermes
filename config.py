import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCNl-G8fKSzuRCY_9CFtCyZ98M4-4Imf8w")
    SAFETY_SETTINGS = {
        'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
        'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
        'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
        'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
    }
    GENERATION_CONFIG = {
        "temperature": 0.7,
        "max_output_tokens": 2000
    }
    MODEL_NAMES = [
        'gemini-1.5-flash',  # New recommended model (fast & affordable)
        'gemini-1.5-pro',    # Higher quality
        'gemini-pro'         # Fallback
    ]