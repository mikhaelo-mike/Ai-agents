import os

from dotenv import load_dotenv


def get_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    return api_key


def get_model_name() -> str:
    load_dotenv()
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
