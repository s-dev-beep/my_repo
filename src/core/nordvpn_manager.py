"""NordVPN Integration for secured data fetching.

Handles NordVPN connection, server rotation, and transparent proxy routing.
"""

import subprocess
import json
import re
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from src.core.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class NordVPNServer:
    """Represents a NordVPN server."""
    hostname: str
    country: str
    ip_address: Optional[str] = None
    status: str = "unknown"


class NordVPNManager:
    """Manage NordVPN connections and server rotation."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        preferred_country: str = "Turkey",
        preferred_server_type: str = "standard",
    ):
        """Initialize NordVPN manager.

        Args:
            username: NordVPN username (or set NORDVPN_USER env var)
            password: NordVPN password (or set NORDVPN_PASS env var)
            preferred_country: Country to connect to (default: Turkey)
            preferred_server_type: Server type: "standard", "p2p", "dedicated"
        """
        import os

        self.username = username or os.getenv("NORDVPN_USER")
        self.password = password or os.getenv("NORDVPN_PASS")
        self.preferred_country = preferred_country
        self.preferred_server_type = preferred_server_type
        self.current_server: Optional[NordVPNServer] = None
        self.is_connected = False
        self.available_servers: List[NordVPNServer] = []

        if not self.username or not self.password:
            logger.warning(
                "NordVPN credentials not provided. Set NORDVPN_USER and NORDVPN_PASS env vars"
            )

    def check_nordvpn_installed(self) -> bool:
        """Check if NordVPN CLI is installed."""
        try:
            result = subprocess.run(
                ["nordvpn", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                logger.info(f"NordVPN CLI found: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        logger.error(
            "NordVPN CLI not installed. Install with: brew install nordvpn (macOS) or apt install nordvpn (Linux)"
        )
        return False

    def login(self) -> bool:
        """Login to NordVPN."""
        if not self.username or not self.password:
            logger.error("NordVPN credentials required for login")
            return False

        logger.info("Logging into NordVPN...")
        try:
            # NordVPN login expects credentials via stdin or environment
            result = subprocess.run(
                ["nordvpn", "login", "--username", self.username, "--password", self.password],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logger.info("✓ Successfully logged into NordVPN")
                return True
            else:
                logger.error(f"Login failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("NordVPN login timed out")
            return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def connect(self, country: Optional[str] = None) -> bool:
        """Connect to NordVPN server.

        Args:
            country: Country to connect to (default: preferred_country)

        Returns:
            True if connected successfully
        """
        country = country or self.preferred_country
        logger.info(f"Connecting to NordVPN ({country})...")

        try:
            result = subprocess.run(
                ["nordvpn", "connect", country],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                self.is_connected = True
                self.current_server = NordVPNServer(
                    hostname=f"nordvpn-{country}",
                    country=country,
                    status="connected",
                )
                logger.info(f"✓ Connected to NordVPN ({country})")
                time.sleep(2)  # Wait for connection to stabilize
                return True
            else:
                logger.error(f"Connection failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("NordVPN connection timed out")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from NordVPN."""
        if not self.is_connected:
            return True

        logger.info("Disconnecting from NordVPN...")

        try:
            result = subprocess.run(
                ["nordvpn", "disconnect"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                self.is_connected = False
                logger.info("✓ Disconnected from NordVPN")
                return True
            else:
                logger.error(f"Disconnect failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("NordVPN disconnect timed out")
            return False
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current NordVPN connection status."""
        try:
            result = subprocess.run(
                ["nordvpn", "status"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                return {
                    "connected": "connected" in output,
                    "status_text": result.stdout.strip(),
                }
            else:
                return {"connected": False, "error": result.stderr}

        except Exception as e:
            return {"connected": False, "error": str(e)}

    def rotate_server(self, country: Optional[str] = None) -> bool:
        """Rotate to a different NordVPN server (reconnect).

        Args:
            country: Country to connect to

        Returns:
            True if rotation successful
        """
        country = country or self.preferred_country
        logger.info(f"Rotating NordVPN server ({country})...")

        # Disconnect first
        self.disconnect()
        time.sleep(1)

        # Reconnect
        return self.connect(country)

    def __enter__(self):
        """Context manager entry."""
        if not self.check_nordvpn_installed():
            raise RuntimeError("NordVPN CLI not installed")

        if not self.login():
            raise RuntimeError("Failed to login to NordVPN")

        if not self.connect():
            raise RuntimeError("Failed to connect to NordVPN")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
