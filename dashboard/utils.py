import os
from pathlib import Path
from dotenv import load_dotenv
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

API_BASE = os.getenv("DASH_API_BASE_URL", "http://127.0.0.1:8000/api/v1")
DEFAULT_TOKEN = os.getenv("DASH_JWT_ACCESS_TOKEN", "").strip()


def api_get(path: str, params: dict | None = None, token: str | None = None) -> dict:
    url = f"{API_BASE}{path}"

    headers = {}
    use_token = (token or DEFAULT_TOKEN).strip() if (token is not None or DEFAULT_TOKEN) else ""
    if use_token:
        headers["Authorization"] = f"Bearer {use_token}"

    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()
