import os
from celery import Celery
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("backend")

# Read CELERY_* settings from Django settings with namespace CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in installed apps
app.autodiscover_tasks()
