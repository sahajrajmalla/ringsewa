import os
import re
import json
import logging
from decimal import Decimal
from io import BytesIO

import requests
import openai 
from django.conf import settings
from .models import Product

from django.conf import settings

BASE_MEDIA_URL = settings.BASE_MEDIA_URL

# Configure logging
logger = logging.getLogger(__name__)

# OpenAI API Keys
OPENAI_KEY = settings.OPENAI_KEY

# Set the OpenAI API key directly (don't instantiate)
openai.api_key = OPENAI_KEY

# Function to download audio from a URL
def download_audio(recording_url):
    """
    Downloads the audio file from the given URL.

    Args:
        recording_url (str): URL of the audio file.

    Returns:
        bytes or None: Binary content of the audio file if successful, else None.
    """
    try:
        response = requests.get(recording_url, timeout=15)
        response.raise_for_status()
        logger.debug(f"Successfully downloaded audio from {recording_url}")
        return response.content
    except requests.RequestException as e:
        logger.error(f"Failed to download audio from {recording_url}: {e}")
        return None

# Function to transcribe audio using OpenAI Whisper
def transcribe_audio(recording_url):
    """
    Transcribes audio using OpenAI's Whisper API.

    Args:
        recording_url (str): URL of the audio file.

    Returns:
        str: Transcribed text or empty string on failure.
    """
    if not OPENAI_KEY:
        logger.error("Whisper API key is not configured.")
        return ""

    audio_content = download_audio(recording_url)
    if not audio_content:
        return ""

    try:
        audio_file = BytesIO(audio_content)
        audio_file.name = "audio.wav"  # Whisper requires a name attribute

        logger.debug(f"Transcribing audio from {recording_url}")
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ne",  # Nepali language code
        )

        # Ensure response contains 'text' attribute
        if hasattr(response, 'text'):
            transcript = response.text.strip()  # Access the 'text' attribute
            logger.debug(f"Transcription successful: {transcript}")
            return transcript
        else:
            logger.error(f"Unexpected response structure: {response}")
            return ""
    except Exception as e:
        logger.error(f"Transcription failed for {recording_url}: {e}")
        return ""

# Function to perform NER using GPT-3
def perform_ner(transcript):
    """
    Performs NER using GPT-3.
    """
    if not OPENAI_KEY:
        logger.error("GPT API key is not configured.")
        return {"product_name": "", "description": "", "price": "", "location": ""}

    prompt = f"""
    Use your AI assistant to extract specific fields from the Nepali text below with your acumen and intuition just like a human would as call center agent.
    
    Extract the following information from the Nepali text below:
    - Product Name
    - Description
    - Price
    - Location

    Text: "{transcript}"

    Provide the output in JSON format like this:
    {{
        "product_name": "",
        "description": "",
        "price": "",
        "location": ""
    }}
    
    Note: Leave empty if the information is not present but do your best to search for it and guess and you can change the text if needed, if transcription is not accurate.
    PS: If you are not sure about the answer, you can leave it empty but reply no matter what.
    """

    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system", "content": "You extract specific fields from Nepali text."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    try:
        logger.debug("Sending transcript for NER")
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
        response.raise_for_status()

        ner_result = response.json()['choices'][0]['message']['content']
        logger.debug(f"NER response: {ner_result}")

        # Parsing NER result: stripping unnecessary characters
        try:
            ner_data = json.loads(ner_result.strip().replace("```json", "").replace("\n```", ""))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse NER response: {e}")
            ner_data = {}

        # Ensure all keys are present and clean up data
        for key in ["product_name", "description", "price", "location"]:
            ner_data.setdefault(key, "")

        ner_data = {k: v.strip() if isinstance(v, str) else v for k, v in ner_data.items()}
        return ner_data

    except requests.RequestException as e:
        logger.error(f"NER request failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during NER: {e}")

    return {"product_name": "", "description": "", "price": "", "location": ""}


# Function to extract and save NER data in the database
def extract_and_save(product_instance):
    """
    This function is called to extract and save NER data in the database.
    It will update the corresponding product instance with the extracted fields.
    """
    # Step 1: Transcribe audio
    recording_url = str(BASE_MEDIA_URL) + str(product_instance.audio_url)  # Assuming the audio URL is stored in the model
    transcript = transcribe_audio(recording_url)

    # Step 2: Perform NER on the transcript
    if transcript:
        ner_data = perform_ner(transcript)
        
        print(ner_data)

        # Step 3: Update product instance with extracted data
        product_instance.audio_transcription = transcript
        product_instance.extracted_product_name = ner_data.get('product_name', '')
        product_instance.extracted_description = ner_data.get('description', '')
        product_instance.extracted_price = ner_data.get('price', '')
        product_instance.extracted_location = ner_data.get('location', '')
        product_instance.pending_transcription = False
        product_instance.pending_ner = False
        
        # Save the updated product instance
        product_instance.save()

        logger.info(f"Product {product_instance.id} updated with NER data.")
    else:
        logger.error(f"Failed to transcribe audio for Product {product_instance.id}.")
