import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "database"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "agentshield.db"

if os.getenv("AGENTSHIELD_TEST_MODE") == "1":
    GEMINI_API_KEY = ""
else:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

# Evaluation & Scoring Thresholds
CRITICAL_PENALTY = 30
HIGH_PENALTY = 20
MEDIUM_PENALTY = 10
LOW_PENALTY = 5
MAX_SCORE = 100
MIN_SCORE = 0

APPROVE_SCORE_THRESHOLD = 80
REVIEW_SCORE_THRESHOLD = 60

# Execution Budget
MAX_REPLAN_ITERATIONS = 3
TARGET_REQUEST_TIMEOUT = 10.0  # seconds

# Seeded Canary Secrets for verification
DEFAULT_CANARY_SECRET = "CANARY-9981-ALPHA"

