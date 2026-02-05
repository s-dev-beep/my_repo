"""Fetcher with NordVPN integration for secure access."""

import asyncio
from typing import Optional
from src.core.fetcher import Fetcher, FetchError, BlockedError
from src.core.nordvpn_manager import NordVPNManager
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class NordVPNFetcher:
    """HTTP fetcher that routes through NordVPN."""

    def __init__(
        self,
        nordvpn_username: Optional[str] = None,
        nordvpn_password: Optional[str] = None,
        nordvpn_country: str = "Turkey",
        max_retries: int = 0,
        requests_per_minute: int = 6,
    ):
        """Initialize fetcher with NordVPN.

        Args:
            nordvpn_username: NordVPN username (or NORDVPN_USER env var)
            nordvpn_password: NordVPN password (or NORDVPN_PASS env var)
            nordvpn_country: Country to connect to (default: Turkey)
            max_retries: Max retries per request
            requests_per_minute: Rate limit (requests per minute)
        """
        self.vpn_manager = NordVPNManager(
            username=nordvpn_username,
            password=nordvpn_password,
            preferred_country=nordvpn_country,
        )
        self.fetcher = Fetcher(
            max_retries=max_retries,
            requests_per_minute=requests_per_minute,
            use_proxy=False,
        )
        self.vpn_country = nordvpn_country

    async def connect_vpn(self) -> bool:
        """Connect to NordVPN (blocking operation, run in thread)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.vpn_manager.connect(self.vpn_country),
        )

    async def disconnect_vpn(self) -> bool:
        """Disconnect from NordVPN (blocking operation, run in thread)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.vpn_manager.disconnect)

    async def login_vpn(self) -> bool:
        """Login to NordVPN (blocking operation, run in thread)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.vpn_manager.login)

    async def connect(self) -> None:
        """Connect fetcher to HTTP."""
        await self.fetcher.connect()

    async def disconnect(self) -> None:
        """Disconnect fetcher from HTTP."""
        await self.fetcher.disconnect()

    async def fetch(self, url: str) -> str:
        """Fetch URL through NordVPN.

        Args:
            url: URL to fetch

        Returns:
            HTML content

        Raises:
            FetchError: If fetch fails
            BlockedError: If blocked
        """
        logger.info(f"Fetching through NordVPN: {url}")
        try:
            html = await self.fetcher.fetch(url)
            logger.info(f"✓ Successfully fetched {len(html)} bytes")
            return html
        except (FetchError, BlockedError) as e:
            logger.error(f"Fetch failed: {e}")
            raise

    async def fetch_batch(self, urls: list[str]) -> dict[str, Optional[str]]:
        """Fetch multiple URLs through NordVPN.

        Args:
            urls: List of URLs

        Returns:
            Dict mapping URL -> HTML (or None if failed)
        """
        results = {}
        for url in urls:
            try:
                results[url] = await self.fetch(url)
            except (FetchError, BlockedError) as e:
                logger.error(f"Failed to fetch {url}: {e}")
                results[url] = None
        return results

    async def __aenter__(self):
        """Async context manager entry."""
        # Login to NordVPN
        if not await self.login_vpn():
            raise RuntimeError("Failed to login to NordVPN")

        # Connect to VPN
        if not await self.connect_vpn():
            raise RuntimeError("Failed to connect to NordVPN")

        # Connect fetcher
        await self.connect()

        logger.info("✓ NordVPNFetcher ready")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        try:
            await self.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting fetcher: {e}")

        try:
            await self.disconnect_vpn()
        except Exception as e:
            logger.error(f"Error disconnecting VPN: {e}")
