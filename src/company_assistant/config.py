import os

from dotenv import load_dotenv


def get_gemini_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    return api_key


def get_gemini_model_name() -> str:
    load_dotenv()
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
