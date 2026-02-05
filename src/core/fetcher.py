"""HTTP fetching module with rate limiting, retries, and polite crawling."""

import asyncio
import random
from typing import Optional, Dict, List
from collections import deque
from datetime import datetime, timedelta
from urllib.parse import urlparse

# aiohttp is required for production
try:
    import aiohttp
except ImportError:
    aiohttp = None  # Will be checked at runtime

from src.core.logger import setup_logger
from src.utils.constants import (
    USER_AGENTS,
    DEFAULT_HEADERS,
    BLOCKING_STATUS_CODES,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF_FACTOR,
    DEFAULT_INITIAL_RETRY_DELAY,
    DEFAULT_REQUESTS_PER_MINUTE,
    DEFAULT_RANDOM_DELAY_MIN,
    DEFAULT_RANDOM_DELAY_MAX,
    DEFAULT_TIMEOUT,
    PROXY_URL,
    USE_PROXY,
    MAX_CONSECUTIVE_BLOCKS,
    BLOCK_THRESHOLD_WINDOW,
)

logger = setup_logger(__name__)


class FetchError(Exception):
    """Base exception for fetch errors."""
    pass


class BlockedError(FetchError):
    """Raised when repeated blocking is detected (403/429)."""
    pass


class Fetcher:
    """Domain-agnostic HTTP fetcher with rate limiting, retries, and backoff."""

    last_status_by_url: Dict[str, Optional[int]]
    
    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
        random_delay_min: float = DEFAULT_RANDOM_DELAY_MIN,
        random_delay_max: float = DEFAULT_RANDOM_DELAY_MAX,
        use_proxy: bool = USE_PROXY,
        proxy_url: Optional[str] = PROXY_URL,
    ):
        """Initialize fetcher with configurable behavior.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            requests_per_minute: Rate limit (requests per minute)
            random_delay_min: Minimum random delay between requests (seconds)
            random_delay_max: Maximum random delay between requests (seconds)
            use_proxy: Whether to use proxy
            proxy_url: Proxy URL (if use_proxy=True)
            
        Raises:
            ValueError: If configuration is invalid
        """
        if requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be > 0")
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        
        self.timeout = timeout
        self.max_retries = max_retries
        self.requests_per_minute = requests_per_minute
        self.random_delay_min = random_delay_min
        self.random_delay_max = random_delay_max
        
        # Rate limiting
        self.min_delay_between_requests = 60.0 / requests_per_minute
        self.last_request_time: Dict[str, float] = {}  # per-domain timing

        # Track last status code per URL (for reporting/experiments)
        self.last_status_by_url: Dict[str, Optional[int]] = {}
        
        # Proxy configuration
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        if use_proxy and not proxy_url:
            raise ValueError("use_proxy=True but proxy_url not provided")
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None if aiohttp else None
        
        # Block detection (per domain)
        self.block_history: Dict[str, deque] = {}  # domain -> deque of block timestamps
        
        logger.info(
            f"Fetcher initialized: timeout={timeout}s, "
            f"max_retries={max_retries}, "
            f"rate_limit={requests_per_minute}req/min, "
            f"proxy={'enabled' if use_proxy else 'disabled'}"
        )
    
    async def connect(self) -> None:
        """Create aiohttp session."""
        if aiohttp is None:
            raise ImportError(
                "aiohttp is required for HTTP fetching. "
                "Install with: pip install aiohttp"
            )
        
        if self.session is None:
            connector = aiohttp.TCPConnector(limit_per_host=1)
            self.session = aiohttp.ClientSession(connector=connector)
            logger.debug("HTTP session created")
    
    async def disconnect(self) -> None:
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.debug("HTTP session closed")
    
    def _get_random_user_agent(self) -> str:
        """Get a random User-Agent string.
        
        Returns:
            Random User-Agent from the pool
        """
        return random.choice(USER_AGENTS)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with random User-Agent.
        
        Returns:
            Headers dictionary
        """
        headers = DEFAULT_HEADERS.copy()
        headers["User-Agent"] = self._get_random_user_agent()
        return headers
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL for rate limiting tracking.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name (e.g., 'sahibinden.com')
        """
        parsed = urlparse(url)
        return parsed.netloc
    
    async def _wait_for_rate_limit(self, domain: str) -> None:
        """Wait to respect rate limits for a specific domain.
        
        Args:
            domain: Domain name
        """
        now = asyncio.get_event_loop().time()
        last_time = self.last_request_time.get(domain, 0)
        elapsed = now - last_time
        
        if elapsed < self.min_delay_between_requests:
            wait_time = self.min_delay_between_requests - elapsed
            logger.debug(f"Rate limit: waiting {wait_time:.2f}s for {domain}")
            await asyncio.sleep(wait_time)
    
    async def _add_random_delay(self) -> None:
        """Add random delay for polite crawling."""
        delay = random.uniform(self.random_delay_min, self.random_delay_max)
        logger.debug(f"Adding random delay: {delay:.2f}s")
        await asyncio.sleep(delay)
    
    def _record_block(self, domain: str) -> None:
        """Record a blocking event for a domain.
        
        Args:
            domain: Domain name
        """
        now = datetime.now()
        
        if domain not in self.block_history:
            self.block_history[domain] = deque()
        
        # Remove old entries outside the window
        while self.block_history[domain]:
            oldest = self.block_history[domain][0]
            if (now - oldest).total_seconds() > BLOCK_THRESHOLD_WINDOW:
                self.block_history[domain].popleft()
            else:
                break
        
        # Add new block event
        self.block_history[domain].append(now)
        
        block_count = len(self.block_history[domain])
        logger.warning(
            f"Block detected for {domain} (status 403/429). "
            f"Recent blocks: {block_count}/{MAX_CONSECUTIVE_BLOCKS}"
        )
    
    def _check_repeated_blocking(self, domain: str) -> None:
        """Check if domain is being repeatedly blocked.
        
        Args:
            domain: Domain name
            
        Raises:
            BlockedError: If repeated blocking detected
        """
        block_count = len(self.block_history.get(domain, []))
        
        if block_count >= MAX_CONSECUTIVE_BLOCKS:
            msg = (
                f"Repeated blocking detected for {domain}: "
                f"{block_count} blocks in {BLOCK_THRESHOLD_WINDOW}s. "
                f"Stopping to respect server limits."
            )
            logger.error(msg)
            raise BlockedError(msg)
    
    async def fetch(self, url: str) -> str:
        """Fetch HTML content from a URL with retries and rate limiting.
        
        Args:
            url: URL to fetch
            
        Returns:
            Raw HTML content as string
            
        Raises:
            FetchError: If fetch fails after all retries
            BlockedError: If repeated blocking is detected
            ValueError: If URL is invalid
        """
        # Validate URL
        if not url or not isinstance(url, str):
            raise ValueError(f"Invalid URL: {url}")
        
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"URL must start with http:// or https://: {url}")
        
        domain = self._get_domain(url)
        
        # Check if domain is being repeatedly blocked
        self._check_repeated_blocking(domain)
        
        # Ensure session is ready
        if not self.session:
            await self.connect()
        
        attempt = 0
        current_delay = DEFAULT_INITIAL_RETRY_DELAY
        
        while attempt <= self.max_retries:
            try:
                # Respect rate limits
                await self._wait_for_rate_limit(domain)
                
                # Add random delay for polite crawling
                await self._add_random_delay()
                
                # Make request
                logger.info(f"Fetching (attempt {attempt + 1}): {url}")
                
                async with self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    proxy=self.proxy_url if self.use_proxy else None,
                    allow_redirects=True,
                ) as response:
                    # Track last status
                    self.last_status_by_url[url] = response.status
                    # Update rate limit timestamp
                    self.last_request_time[domain] = asyncio.get_event_loop().time()
                    
                    # Check for blocking
                    if response.status in BLOCKING_STATUS_CODES:
                        self._record_block(domain)
                        self._check_repeated_blocking(domain)
                        
                        # Backoff on blocking
                        if attempt < self.max_retries:
                            logger.warning(
                                f"Got status {response.status}, backing off "
                                f"and retrying ({attempt + 1}/{self.max_retries})"
                            )
                            await asyncio.sleep(current_delay)
                            current_delay *= DEFAULT_RETRY_BACKOFF_FACTOR
                            attempt += 1
                            continue
                        else:
                            raise FetchError(
                                f"Status {response.status} after {self.max_retries} retries"
                            )
                    
                    # Handle other HTTP errors
                    if response.status >= 400:
                        raise FetchError(
                            f"HTTP {response.status} for {url}"
                        )
                    
                    # Success
                    html = await response.text()
                    logger.info(
                        f"Successfully fetched {len(html)} bytes from {url}"
                    )
                    return html
                    
            except asyncio.TimeoutError:
                self.last_status_by_url[url] = None
                attempt += 1
                if attempt <= self.max_retries:
                    logger.warning(
                        f"Timeout on {url}, retrying "
                        f"({attempt}/{self.max_retries}) after {current_delay}s"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= DEFAULT_RETRY_BACKOFF_FACTOR
                else:
                    raise FetchError(f"Timeout after {self.max_retries} retries: {url}")
            
            except aiohttp.ClientError as e:
                self.last_status_by_url[url] = None
                attempt += 1
                if attempt <= self.max_retries:
                    logger.warning(
                        f"Network error on {url}: {e}. "
                        f"Retrying ({attempt}/{self.max_retries}) after {current_delay}s"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= DEFAULT_RETRY_BACKOFF_FACTOR
                else:
                    raise FetchError(f"Network error after {self.max_retries} retries: {e}")
        
        raise FetchError(f"Failed to fetch {url} after {self.max_retries} retries")

    def get_last_status(self, url: str) -> Optional[int]:
        """Return the last HTTP status code recorded for a URL."""
        return self.last_status_by_url.get(url)
    
    async def fetch_batch(self, urls: list) -> Dict[str, Optional[str]]:
        """Fetch multiple URLs, returning results even if some fail.
        
        Args:
            urls: List of URLs to fetch
            
        Returns:
            Dictionary mapping URL -> HTML content (or None if failed)
        """
        results = {}
        
        for url in urls:
            try:
                results[url] = await self.fetch(url)
            except (FetchError, BlockedError) as e:
                logger.error(f"Failed to fetch {url}: {e}")
                results[url] = None
            except KeyboardInterrupt:
                logger.warning("Fetch batch interrupted by user")
                raise
        
        return results
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()
from src.utils.constants import (
    USER_AGENTS,
    DEFAULT_HEADERS,
    BLOCKING_STATUS_CODES,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF_FACTOR,
    DEFAULT_INITIAL_RETRY_DELAY,
    DEFAULT_REQUESTS_PER_MINUTE,
    DEFAULT_RANDOM_DELAY_MIN,
    DEFAULT_RANDOM_DELAY_MAX,
    DEFAULT_TIMEOUT,
    PROXY_URL,
    USE_PROXY,
    MAX_CONSECUTIVE_BLOCKS,
    BLOCK_THRESHOLD_WINDOW,
)

logger = setup_logger(__name__)


class FetchError(Exception):
    """Base exception for fetch errors."""
    pass


class BlockedError(FetchError):
    """Raised when repeated blocking is detected (403/429)."""
    pass


class Fetcher:
    """Domain-agnostic HTTP fetcher with rate limiting, retries, and backoff."""
    
    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
        random_delay_min: float = DEFAULT_RANDOM_DELAY_MIN,
        random_delay_max: float = DEFAULT_RANDOM_DELAY_MAX,
        use_proxy: bool = USE_PROXY,
        proxy_url: Optional[str] = PROXY_URL,
    ):
        """Initialize fetcher with configurable behavior.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            requests_per_minute: Rate limit (requests per minute)
            random_delay_min: Minimum random delay between requests (seconds)
            random_delay_max: Maximum random delay between requests (seconds)
            use_proxy: Whether to use proxy
            proxy_url: Proxy URL (if use_proxy=True)
            
        Raises:
            ValueError: If configuration is invalid
        """
        if requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be > 0")
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        
        self.timeout = timeout
        self.max_retries = max_retries
        self.requests_per_minute = requests_per_minute
        self.random_delay_min = random_delay_min
        self.random_delay_max = random_delay_max
        
        # Rate limiting
        self.min_delay_between_requests = 60.0 / requests_per_minute
        self.last_request_time: Dict[str, float] = {}  # per-domain timing
        
        # Proxy configuration
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        if use_proxy and not proxy_url:
            raise ValueError("use_proxy=True but proxy_url not provided")
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Block detection (per domain)
        self.block_history: Dict[str, deque] = {}  # domain -> deque of block timestamps
        
        logger.info(
            f"Fetcher initialized: timeout={timeout}s, "
            f"max_retries={max_retries}, "
            f"rate_limit={requests_per_minute}req/min, "
            f"proxy={'enabled' if use_proxy else 'disabled'}"
        )
    
    async def connect(self) -> None:
        """Create aiohttp session."""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit_per_host=1)
            self.session = aiohttp.ClientSession(connector=connector)
            logger.debug("HTTP session created")
    
    async def disconnect(self) -> None:
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.debug("HTTP session closed")
    
    def _get_random_user_agent(self) -> str:
        """Get a random User-Agent string.
        
        Returns:
            Random User-Agent from the pool
        """
        return random.choice(USER_AGENTS)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with random User-Agent.
        
        Returns:
            Headers dictionary
        """
        headers = DEFAULT_HEADERS.copy()
        headers["User-Agent"] = self._get_random_user_agent()
        return headers
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL for rate limiting tracking.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name (e.g., 'sahibinden.com')
        """
        parsed = urlparse(url)
        return parsed.netloc
    
    async def _wait_for_rate_limit(self, domain: str) -> None:
        """Wait to respect rate limits for a specific domain.
        
        Args:
            domain: Domain name
        """
        now = asyncio.get_event_loop().time()
        last_time = self.last_request_time.get(domain, 0)
        elapsed = now - last_time
        
        if elapsed < self.min_delay_between_requests:
            wait_time = self.min_delay_between_requests - elapsed
            logger.debug(f"Rate limit: waiting {wait_time:.2f}s for {domain}")
            await asyncio.sleep(wait_time)
    
    async def _add_random_delay(self) -> None:
        """Add random delay for polite crawling."""
        delay = random.uniform(self.random_delay_min, self.random_delay_max)
        logger.debug(f"Adding random delay: {delay:.2f}s")
        await asyncio.sleep(delay)
    
    def _record_block(self, domain: str) -> None:
        """Record a blocking event for a domain.
        
        Args:
            domain: Domain name
        """
        now = datetime.now()
        
        if domain not in self.block_history:
            self.block_history[domain] = deque()
        
        # Remove old entries outside the window
        while self.block_history[domain]:
            oldest = self.block_history[domain][0]
            if (now - oldest).total_seconds() > BLOCK_THRESHOLD_WINDOW:
                self.block_history[domain].popleft()
            else:
                break
        
        # Add new block event
        self.block_history[domain].append(now)
        
        block_count = len(self.block_history[domain])
        logger.warning(
            f"Block detected for {domain} (status 403/429). "
            f"Recent blocks: {block_count}/{MAX_CONSECUTIVE_BLOCKS}"
        )
    
    def _check_repeated_blocking(self, domain: str) -> None:
        """Check if domain is being repeatedly blocked.
        
        Args:
            domain: Domain name
            
        Raises:
            BlockedError: If repeated blocking detected
        """
        block_count = len(self.block_history.get(domain, []))
        
        if block_count >= MAX_CONSECUTIVE_BLOCKS:
            msg = (
                f"Repeated blocking detected for {domain}: "
                f"{block_count} blocks in {BLOCK_THRESHOLD_WINDOW}s. "
                f"Stopping to respect server limits."
            )
            logger.error(msg)
            raise BlockedError(msg)
    
    async def fetch(self, url: str) -> str:
        """Fetch HTML content from a URL with retries and rate limiting.
        
        Args:
            url: URL to fetch
            
        Returns:
            Raw HTML content as string
            
        Raises:
            FetchError: If fetch fails after all retries
            BlockedError: If repeated blocking is detected
            ValueError: If URL is invalid
        """
        # Validate URL
        if not url or not isinstance(url, str):
            raise ValueError(f"Invalid URL: {url}")
        
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"URL must start with http:// or https://: {url}")
        
        domain = self._get_domain(url)
        
        # Check if domain is being repeatedly blocked
        self._check_repeated_blocking(domain)
        
        # Ensure session is ready
        if not self.session:
            await self.connect()
        
        attempt = 0
        current_delay = DEFAULT_INITIAL_RETRY_DELAY
        
        while attempt <= self.max_retries:
            try:
                # Respect rate limits
                await self._wait_for_rate_limit(domain)
                
                # Add random delay for polite crawling
                await self._add_random_delay()
                
                # Make request
                logger.info(f"Fetching (attempt {attempt + 1}): {url}")
                
                async with self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    proxy=self.proxy_url if self.use_proxy else None,
                    allow_redirects=True,
                ) as response:
                    # Update rate limit timestamp
                    self.last_request_time[domain] = asyncio.get_event_loop().time()
                    
                    # Check for blocking
                    if response.status in BLOCKING_STATUS_CODES:
                        self._record_block(domain)
                        self._check_repeated_blocking(domain)
                        
                        # Backoff on blocking
                        if attempt < self.max_retries:
                            logger.warning(
                                f"Got status {response.status}, backing off "
                                f"and retrying ({attempt + 1}/{self.max_retries})"
                            )
                            await asyncio.sleep(current_delay)
                            current_delay *= DEFAULT_RETRY_BACKOFF_FACTOR
                            attempt += 1
                            continue
                        else:
                            raise FetchError(
                                f"Status {response.status} after {self.max_retries} retries"
                            )
                    
                    # Handle other HTTP errors
                    if response.status >= 400:
                        raise FetchError(
                            f"HTTP {response.status} for {url}"
                        )
                    
                    # Success
                    html = await response.text()
                    logger.info(
                        f"Successfully fetched {len(html)} bytes from {url}"
                    )
                    return html
                    
            except asyncio.TimeoutError:
                attempt += 1
                if attempt <= self.max_retries:
                    logger.warning(
                        f"Timeout on {url}, retrying "
                        f"({attempt}/{self.max_retries}) after {current_delay}s"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= DEFAULT_RETRY_BACKOFF_FACTOR
                else:
                    raise FetchError(f"Timeout after {self.max_retries} retries: {url}")
            
            except aiohttp.ClientError as e:
                attempt += 1
                if attempt <= self.max_retries:
                    logger.warning(
                        f"Network error on {url}: {e}. "
                        f"Retrying ({attempt}/{self.max_retries}) after {current_delay}s"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= DEFAULT_RETRY_BACKOFF_FACTOR
                else:
                    raise FetchError(f"Network error after {self.max_retries} retries: {e}")
        
        raise FetchError(f"Failed to fetch {url} after {self.max_retries} retries")
    
    async def fetch_batch(self, urls: list) -> Dict[str, Optional[str]]:
        """Fetch multiple URLs, returning results even if some fail.
        
        Args:
            urls: List of URLs to fetch
            
        Returns:
            Dictionary mapping URL -> HTML content (or None if failed)
        """
        results = {}
        
        for url in urls:
            try:
                results[url] = await self.fetch(url)
            except (FetchError, BlockedError) as e:
                logger.error(f"Failed to fetch {url}: {e}")
                results[url] = None
            except KeyboardInterrupt:
                logger.warning("Fetch batch interrupted by user")
                raise
        
        return results
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()
