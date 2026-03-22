# src/backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # charge le .env à la racine

HF_TOKEN = os.getenv("HF_TOKEN", "")
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN