"""Load URLs, config, and parser for CLI commands.

STEP 11: Command Line Interface

This module handles loading of:
- URL lists from files
- YAML configuration
- Parser instances based on domain detection
"""

from pathlib import Path
from typing import List, Optional
import yaml
import os

from src.core.logger import setup_logger
from src.adapters.sahibinden.parser import SahibindenParser
from src.adapters.hepsiemlak.parser import HepsiemlakParser

logger = setup_logger(__name__)


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from a text file.
    
    Args:
        file_path: Path to file containing URLs (one per line)
    
    Returns:
        List of URLs (stripped, non-empty lines)
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or contains no valid URLs
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"URL file not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    
    logger.info(f"Loading URLs from: {file_path}")
    
    urls = []
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            # Strip whitespace and skip empty lines
            url = line.strip()
            if url and not url.startswith('#'):  # Skip comments
                urls.append(url)
    
    if not urls:
        raise ValueError(f"No valid URLs found in: {file_path}")
    
    logger.info(f"Loaded {len(urls)} URLs from {file_path}")
    return urls


def load_config_file(config_path: Optional[str] = None) -> dict:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to config file (uses default if None)
    
    Returns:
        Configuration dictionary
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    if config_path:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        logger.info(f"Loading config from: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not config:
            raise ValueError(f"Empty or invalid config file: {config_path}")
        
        return config
    
    # Use default config
    default_config_path = Path("config/default.yaml")
    
    if not default_config_path.exists():
        # Return minimal default config if file doesn't exist
        logger.warning("Default config not found, using minimal defaults")
        return {
            'crawler': {
                'run_mode': 'full_run',
                'safety': {
                    'max_fetch_failure_rate': 0.5,
                    'max_consecutive_blocks': 5,
                    'max_quality_rejection_rate': 0.7,
                    'min_urls_before_checks': 10,
                }
            },
            'database': {
                'mongo_uri': os.getenv('MONGO_URI'),
                'db_name': 'real_estate_crawler',
            }
        }
    
    logger.info(f"Loading default config from: {default_config_path}")
    with open(default_config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def detect_parser_type(urls: List[str]) -> str:
    """Detect parser type from URLs.
    
    Args:
        urls: List of URLs to analyze
    
    Returns:
        Parser type ('sahibinden' or 'hepsiemlak')
    
    Raises:
        ValueError: If URLs are mixed or from unknown domain
    """
    if not urls:
        raise ValueError("Cannot detect parser type: no URLs provided")
    
    # Check first URL
    first_url = urls[0].lower()
    
    if 'sahibinden.com' in first_url:
        parser_type = 'sahibinden'
    elif 'hepsiemlak.com' in first_url:
        parser_type = 'hepsiemlak'
    else:
        raise ValueError(
            f"Unknown domain in URL: {urls[0]}\n"
            "Supported domains: sahibinden.com, hepsiemlak.com"
        )
    
    # Validate all URLs are from same domain
    for url in urls:
        url_lower = url.lower()
        if parser_type == 'sahibinden' and 'sahibinden.com' not in url_lower:
            raise ValueError(
                f"Mixed domains detected. Expected sahibinden.com, got: {url}"
            )
        elif parser_type == 'hepsiemlak' and 'hepsiemlak.com' not in url_lower:
            raise ValueError(
                f"Mixed domains detected. Expected hepsiemlak.com, got: {url}"
            )
    
    logger.info(f"Detected parser type: {parser_type}")
    return parser_type


def create_parser(parser_type: str):
    """Create parser instance for given type.
    
    Args:
        parser_type: Parser type ('sahibinden' or 'hepsiemlak')
    
    Returns:
        Parser instance
    
    Raises:
        ValueError: If parser type is unknown
    """
    if parser_type == 'sahibinden':
        logger.info("Creating SahibindenParser instance")
        return SahibindenParser()
    elif parser_type == 'hepsiemlak':
        logger.info("Creating HepsiemlakParser instance")
        return HepsiemlakParser()
    else:
        raise ValueError(
            f"Unknown parser type: {parser_type}\n"
            "Supported types: sahibinden, hepsiemlak"
        )
