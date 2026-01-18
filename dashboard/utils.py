import os
from pathlib import Path
from dotenv import load_dotenv
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

API_BASE = os.getenv("DASH_API_BASE_URL", "http://127.0.0.1:8000/api/v1")


def api_get(path: str, params: dict | None = None) -> dict:
    url = f"{API_BASE}{path}"
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()
