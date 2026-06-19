import logging
from datetime import datetime
 
# ========================
# LOGGER SETUP
# ========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
 
logger = logging.getLogger(__name__)
 
 
# ========================
# CONSTANTS
# ========================
DEFAULT_LANGUAGE = "en"
MAX_NEWS_LIMIT = 20
 
 
# ========================
# HELPER FUNCTIONS
# ========================
 
def format_datetime(dt: datetime):
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")
 
 
def time_ago(dt: datetime):
    if not dt:
        return None
 
    now = datetime.utcnow()
    diff = now - dt
 
    seconds = diff.total_seconds()
 
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    else:
        return f"{int(seconds // 86400)} days ago"
 