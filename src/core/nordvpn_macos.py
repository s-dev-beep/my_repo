"""Alternative NordVPN solution using OpenVPN for macOS.

Since NordVPN macOS app doesn't provide CLI, we'll use OpenVPN directly.
"""

import subprocess
import os
import requests
from pathlib import Path
from typing import Optional
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class NordVPNMacOS:
    """NordVPN connector for macOS using OpenVPN."""
    
    def __init__(self, username: str, password: str):
        """Initialize with NordVPN credentials.
        
        Args:
            username: NordVPN email
            password: NordVPN password
        """
        self.username = username
        self.password = password
        self.config_dir = Path.home() / ".nordvpn"
        self.config_dir.mkdir(exist_ok=True)
        
    def download_turkey_config(self) -> Path:
        """Download Turkey OpenVPN config from NordVPN.
        
        Returns:
            Path to the downloaded config file
        """
        # Get recommended Turkey server
        logger.info("Getting recommended Turkey server...")
        response = requests.get(
            "https://api.nordvpn.com/v1/servers/recommendations",
            params={"filters[country_id]": 43, "limit": 1}  # 43 = Turkey
        )
        response.raise_for_status()
        
        server = response.json()[0]
        hostname = server["hostname"]
        
        logger.info(f"Using server: {hostname}")
        
        # Download OpenVPN config
        config_url = f"https://downloads.nordcdn.com/configs/files/ovpn_tcp/servers/{hostname}.tcp.ovpn"
        config_response = requests.get(config_url)
        config_response.raise_for_status()
        
        # Save config
        config_path = self.config_dir / "turkey.ovpn"
        config_path.write_text(config_response.text)
        
        logger.info(f"Config saved to {config_path}")
        return config_path
    
    def create_auth_file(self) -> Path:
        """Create authentication file for OpenVPN.
        
        Returns:
            Path to auth file
        """
        auth_path = self.config_dir / "auth.txt"
        auth_path.write_text(f"{self.username}\n{self.password}\n")
        auth_path.chmod(0o600)  # Secure permissions
        return auth_path
    
    def connect(self) -> bool:
        """Connect to Turkey VPN using OpenVPN.
        
        Returns:
            True if connected successfully
        """
        # Check if OpenVPN is installed
        try:
            subprocess.run(["which", "openvpn"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            logger.error("OpenVPN not installed. Install with: brew install openvpn")
            return False
        
        # Download config
        config_path = self.download_turkey_config()
        auth_path = self.create_auth_file()
        
        # Connect
        logger.info("Connecting to NordVPN Turkey server...")
        cmd = [
            "sudo", "openvpn",
            "--config", str(config_path),
            "--auth-user-pass", str(auth_path),
            "--daemon"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✓ Connected to NordVPN Turkey")
            return True
        else:
            logger.error(f"Connection failed: {result.stderr}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from VPN.
        
        Returns:
            True if disconnected successfully
        """
        result = subprocess.run(["sudo", "killall", "openvpn"], capture_output=True)
        if result.returncode == 0:
            logger.info("✓ Disconnected from NordVPN")
            return True
        return False


# Simple usage example
if __name__ == "__main__":
    import os
    
    username = os.getenv("NORDVPN_USER")
    password = os.getenv("NORDVPN_PASS")
    
    if not username or not password:
        print("Set NORDVPN_USER and NORDVPN_PASS environment variables")
        exit(1)
    
    vpn = NordVPNMacOS(username, password)
    
    print("Connecting to NordVPN Turkey...")
    if vpn.connect():
        print("✓ Connected! Test your connection:")
        print("  curl https://ipinfo.io")
        print("\nDisconnect with: sudo killall openvpn")
    else:
        print("✗ Connection failed")
