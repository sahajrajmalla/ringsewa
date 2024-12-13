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

# Configure logging
logger = logging.getLogger(__name__)

# OpenAI API Keys
WHISPER_API_KEY = settings.OPENAI_WHISPER_API_KEY
GPT0_API_KEY = settings.OPENAI_GPT4O_API_KEY

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

def transcribe_audio(recording_url):
    """
    Transcribes audio using OpenAI's Whisper API.

    Args:
        recording_url (str): URL of the audio file.

    Returns:
        str: Transcribed text or empty string on failure.
    """
    if not WHISPER_API_KEY:
        logger.error("Whisper API key is not configured.")
        return ""

    audio_content = download_audio(recording_url)
    if not audio_content:
        return ""

    try:
        audio_file = BytesIO(audio_content)
        audio_file.name = "audio.wav"  # Whisper requires a name attribute

        logger.debug(f"Transcribing audio from {recording_url}")
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            language="ne",  # Nepali language code
            api_key=WHISPER_API_KEY
        )
        transcript = response.get('text', '').strip()
        logger.debug(f"Transcription successful: {transcript}")
        return transcript
    except Exception as e:
        logger.error(f"Transcription failed for {recording_url}: {e}")
        return ""

def perform_ner(transcript):
    """
    Performs NER using GPT0.

    Args:
        transcript (str): Transcribed text.

    Returns:
        dict: Extracted fields {'product_name': str, 'description': str, 'price': str, 'location': str}.
    """
    if not GPT0_API_KEY:
        logger.error("GPT0 API key is not configured.")
        return {"product_name": "", "description": "", "price": "", "location": ""}

    prompt = f"""
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
    """

    headers = {
        "Authorization": f"Bearer {GPT0_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
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

        ner_data = json.loads(ner_result)
        # Ensure all keys are present
        for key in ["product_name", "description", "price", "location"]:
            ner_data.setdefault(key, "")

        # Clean extracted data
        ner_data = {k: v.strip() if isinstance(v, str) else v for k, v in ner_data.items()}
        return ner_data
    except requests.RequestException as e:
        logger.error(f"NER request failed: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse NER response: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during NER: {e}")

    return {"product_name": "", "description": "", "price": "", "location": ""}

def extract_price(price_input):
    """
    Extracts and parses price from string.

    Args:
        price_input (str): Price string.

    Returns:
        Decimal: Parsed price or Decimal('0.00') on failure.
    """
    match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', price_input)
    if match:
        price_str = match.group(1).replace(',', '')
        try:
            price = Decimal(price_str)
            logger.debug(f"Extracted price: {price}")
            return price
        except:
            logger.error(f"Invalid price format: {price_str}")
    else:
        logger.warning(f"No price found in input: {price_input}")
    return Decimal('0.00')

def extract_and_save(call_sid):
    """
    Orchestrates the transcription and NER workflow for a given call_sid.

    Args:
        call_sid (str): Unique identifier for the call.

    Returns:
        bool: True if both transcription and NER are successful, False otherwise.
    """
    try:
        product = Product.objects.get(call_sid=call_sid)
        logger.info(f"Initiating processing for Call SID: {call_sid}")

        # Step 1: Transcription
        if product.pending_transcription:
            # Transcribe Product Name
            if product.product_name_audio and not product.product_name_text:
                transcript = transcribe_audio(product.product_name_audio.url)
                if transcript:
                    product.product_name_text = transcript
                else:
                    logger.error(f"Failed to transcribe product name for Call SID: {call_sid}")

            # Transcribe Description
            if product.description_audio and not product.description_text:
                transcript = transcribe_audio(product.description_audio.url)
                if transcript:
                    product.description_text = transcript
                else:
                    logger.error(f"Failed to transcribe description for Call SID: {call_sid}")

            # Transcribe Price
            if product.price_audio and not product.price_text:
                transcript = transcribe_audio(product.price_audio.url)
                if transcript:
                    product.price_text = transcript
                else:
                    logger.error(f"Failed to transcribe price for Call SID: {call_sid}")

            # Transcribe Location if audio is provided
            if product.location_audio and not product.location_text:
                transcript = transcribe_audio(product.location_audio.url)
                if transcript:
                    product.location_text = transcript
                else:
                    logger.error(f"Failed to transcribe location for Call SID: {call_sid}")

            # Update transcription status
            product.pending_transcription = False
            product.pending_ner = True
            product.save()
            logger.info(f"Transcription completed for Call SID: {call_sid}")

        # Step 2: NER
        if product.pending_ner:
            # Combine transcribed texts for NER
            full_text = f"{product.product_name_text} {product.description_text} {product.price_text} {product.location_text or ''}"
            ner_data = perform_ner(full_text)

            # Extract and save NER data
            extracted_product_name = ner_data.get('product_name', '').strip()
            extracted_description = ner_data.get('description', '').strip()
            extracted_price_input = ner_data.get('price', '').strip()
            extracted_location = ner_data.get('location', '').strip()

            if extracted_product_name:
                product.extracted_product_name = extracted_product_name
            else:
                logger.warning(f"No product name extracted for Call SID: {call_sid}")

            if extracted_description:
                product.extracted_description = extracted_description
            else:
                logger.warning(f"No description extracted for Call SID: {call_sid}")

            # Extract and parse price
            product.extracted_price = extract_price(extracted_price_input)

            if extracted_location:
                product.extracted_location = extracted_location
            else:
                logger.warning(f"No location extracted for Call SID: {call_sid}")

            # Update NER status
            product.pending_ner = False
            product.processed = True
            product.save()
            logger.info(f"NER completed for Call SID: {call_sid}")

        return True
    except Product.DoesNotExist:
        logger.error(f"No Product found with Call SID: {call_sid}")
    except Exception as e:
        logger.error(f"Unexpected error during processing for Call SID {call_sid}: {e}")

    return False
