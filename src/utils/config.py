"""Configuration loading utilities."""

import os
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize config manager.
        
        Args:
            config_dir: Directory containing config files
        """
        # TODO: Load .env file
        # TODO: Load YAML configs
        # TODO: Merge and validate configuration
        
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        
        logger.info(f"ConfigManager initialized with dir: {config_dir}")
    
    def load_env(self, env_file: str = ".env") -> None:
        """Load environment variables from .env file.
        
        Args:
            env_file: Path to .env file
        """
        # TODO: Use python-dotenv to load environment
        
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
    
    def load_yaml(self, config_file: str) -> Dict[str, Any]:
        """Load YAML configuration file.
        
        Args:
            config_file: Name of YAML file in config directory
            
        Returns:
            Loaded configuration dictionary
        """
        # TODO: Parse YAML with proper error handling
        
        config_path = self.config_dir / config_file
        logger.info(f"Loading config from {config_path}")
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def get_config(self) -> Dict[str, Any]:
        """Get merged configuration.
        
        Returns:
            Configuration dictionary
        """
        # TODO: Merge environment variables with file-based config
        # TODO: Validate against schema
        
        return self.config


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value from environment.
    
    Args:
        key: Configuration key
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    # TODO: Support nested keys (e.g., "database.url")
    
    return os.getenv(key, default)
