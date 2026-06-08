"""
app/agent.py
Gemini API Client wrapper using the Google Gen AI Python SDK.
Handles client initialization, content generation, and structured outputs.
"""

import logging
from typing import Any
from google import genai
from google.genai import types
from app import config

logger = logging.getLogger(__name__)

def get_client() -> genai.Client:
    """
    Initializes and returns the Google Gen AI client using configured api_key.
    """
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set or empty in .env.")
    return genai.Client(api_key=config.GEMINI_API_KEY)

def generate_response(
    system_instruction: str,
    prompt: str,
    model: str = None
) -> str:
    """
    Sends prompt and system instruction parameters to the Gemini API.
    Falls back to GEMINI_FALLBACK_MODEL if the primary model fails.
    """
    if model is None:
        model = config.GEMINI_MODEL

    client = get_client()
    config_params = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
    )

    try:
        logger.info(f"Calling Gemini model {model}...")
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config_params
        )
        return response.text
    except Exception as e:
        logger.error(f"Error calling primary model {model}: {e}")
        
        if model == config.GEMINI_FALLBACK_MODEL:
            raise e
            
        logger.warning(f"Attempting fallback to {config.GEMINI_FALLBACK_MODEL}...")
        try:
            config_params_fallback = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            )
            response = client.models.generate_content(
                model=config.GEMINI_FALLBACK_MODEL,
                contents=prompt,
                config=config_params_fallback
            )
            return response.text
        except Exception as fallback_err:
            logger.error(f"Fallback model call failed: {fallback_err}")
            raise fallback_err

def generate_structured_response(
    system_instruction: str,
    prompt: str,
    response_schema: Any,
    model: str = None
) -> str:
    """
    Sends a request to the Gemini API requiring JSON response conforming to response_schema.
    Returns the raw JSON text response.
    """
    if model is None:
        model = config.GEMINI_MODEL

    client = get_client()
    config_params = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.1,
        response_mime_type="application/json",
        response_schema=response_schema
    )

    try:
        logger.info(f"Calling Gemini model {model} for structured output...")
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config_params
        )
        return response.text
    except Exception as e:
        logger.error(f"Error calling primary model {model} for structured output: {e}")
        
        if model == config.GEMINI_FALLBACK_MODEL:
            raise e
            
        logger.warning(f"Attempting fallback structured call to {config.GEMINI_FALLBACK_MODEL}...")
        try:
            config_params_fallback = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=response_schema
            )
            response = client.models.generate_content(
                model=config.GEMINI_FALLBACK_MODEL,
                contents=prompt,
                config=config_params_fallback
            )
            return response.text
        except Exception as fallback_err:
            logger.error(f"Fallback model call failed: {fallback_err}")
            raise fallback_err