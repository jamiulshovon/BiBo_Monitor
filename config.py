import os
from dotenv import load_dotenv

load_dotenv()

# Admin target URL
TARGET_URL = os.getenv("BIBO_TARGET_URL") or "https://bibotracker.com/admin"

# Optional credentials for automatic re-login if session expires
BIBO_EMAIL = os.getenv("BIBO_EMAIL", "")
BIBO_PASSWORD = os.getenv("BIBO_PASSWORD", "")

# Output directory for screenshots
SCREENSHOTS_DIR = os.getenv("SCREENSHOTS_DIR", "screenshots")

# File path to save session/cookies
AUTH_STATE_PATH = os.getenv("AUTH_STATE_PATH", "auth_state.json")

# Bangladesh Timezone
TIMEZONE = "Asia/Dhaka"

# Browser viewport (defaults to 1920x1600 to fit all employee rows)
VIEWPORT = {
    "width": int(os.getenv("VIEWPORT_WIDTH", "1920")),
    "height": int(os.getenv("VIEWPORT_HEIGHT", "1600"))
}

# Zoom level (defaults to "100%", can be customized if needed)
ZOOM_LEVEL = os.getenv("ZOOM_LEVEL", "100%")

# Scheduled times in 24h format (Bangladesh local time: 6:10 AM, 8:20 AM, 12:55 PM, 2:00 PM)
SCHEDULE_TIMES = ["06:10", "08:20", "12:55", "14:00"]

# Dedicated time folders inside screenshots/
TIME_FOLDERS = [
    "06-10_AM",
    "08-20_AM",
    "12-55_PM",
    "02-00_PM"
]
