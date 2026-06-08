"""
app/config.py
Configuration loader for Gemini Agent OS.
Loads settings from environment variables and the root .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if it exists
env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

# App Configurations
APP_ENV = os.getenv("APP_ENV", "local")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")

try:
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
except ValueError:
    APP_PORT = 8000

# Resolve Data Layer Root Path (AGENT_ROOT)
# We fall back to the project root directory if AGENT_ROOT is not set or invalid.
agent_root_env = os.getenv("AGENT_ROOT")
if agent_root_env:
    AGENT_ROOT = Path(agent_root_env).resolve()
else:
    agent_data_env = os.getenv("AGENT_DATA_DIR")
    if agent_data_env:
        AGENT_ROOT = Path(agent_data_env).resolve().parent
    else:
        AGENT_ROOT = ROOT_DIR

TIMEZONE = os.getenv("TIMEZONE", "America/Chicago")

# Gemini Configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")

# URLs and Secrets
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")
AUTH_SHARED_SECRET = os.getenv("AUTH_SHARED_SECRET", "replace_me_for_v0")