import os

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
DEFAULT_DAYS: int = 30
DATE_FORMAT: str = "%Y-%m-%d"
MARKETPLACES: list[str] = ["ALL", "WB", "OZON"]

REQUEST_TIMEOUT_SECONDS: float = 10.0
CACHE_TTL_SECONDS: int = 300

COLOR_WB: str = "#8055F5"
COLOR_OZON: str = "#005BFF"
COLOR_PROFIT: str = "#1DB954"
COLOR_LOSS: str = "#E74C3C"
