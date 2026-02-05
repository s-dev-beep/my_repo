"""Constants and configuration for crawling."""

import os

# User-Agent pool for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0",
]

# Common request headers
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# HTTP status codes that indicate blocking
BLOCKING_STATUS_CODES = {
    403,  # Forbidden
    429,  # Too Many Requests
}

# Retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_FACTOR = 2.0  # Exponential backoff multiplier
DEFAULT_INITIAL_RETRY_DELAY = 1.0  # seconds

# Rate limiting configuration
DEFAULT_REQUESTS_PER_MINUTE = 10
DEFAULT_RANDOM_DELAY_MIN = 1.0  # seconds
DEFAULT_RANDOM_DELAY_MAX = 3.0  # seconds

# Timeout
DEFAULT_TIMEOUT = 30  # seconds

# Proxy configuration from environment
PROXY_URL = os.getenv("PROXY_URL", None)
USE_PROXY = os.getenv("USE_PROXY", "false").lower() == "true"

# Blocking detection
MAX_CONSECUTIVE_BLOCKS = 3  # Stop if blocked 3+ times in a row
BLOCK_THRESHOLD_WINDOW = 60  # seconds - track blocks in this window
