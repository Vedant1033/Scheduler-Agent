"""Backend LLM API wrapper."""

import requests

from config import GEMINI_API_URL


def generate_gemini_api(prompt: str, text: str) -> str:
    """Call the TPA text-generation API and return the response string."""
    data = {"prompt": prompt, "ocr_text": text}
    res = requests.post(GEMINI_API_URL, json=data)
    return res.json()
