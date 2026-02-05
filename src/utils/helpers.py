"""Helper utilities for common operations."""

import asyncio
from typing import Callable, Any, TypeVar, Coroutine
from datetime import datetime, timedelta

from src.core.logger import setup_logger

logger = setup_logger(__name__)

T = TypeVar("T")


async def retry_async(
    func: Callable[..., Coroutine],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    *args,
    **kwargs,
) -> Any:
    """Execute async function with exponential backoff retry.
    
    Args:
        func: Async function to execute
        max_retries: Maximum number of retries
        delay: Initial delay in seconds
        backoff: Backoff multiplier
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        Exception: If all retries fail
    """
    # TODO: Implement exponential backoff logic
    
    attempt = 0
    current_delay = delay
    
    while attempt < max_retries:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            attempt += 1
            if attempt >= max_retries:
                logger.error(f"Retry failed after {max_retries} attempts: {e}")
                raise
            
            logger.warning(f"Attempt {attempt} failed, retrying in {current_delay}s: {e}")
            await asyncio.sleep(current_delay)
            current_delay *= backoff


def parse_price(price_str: str) -> float:
    """Parse price string to float.
    
    Args:
        price_str: Price string (e.g., "1.500.000 TL", "2,500")
        
    Returns:
        Float price value
    """
    # TODO: Handle various price formats
    # TODO: Handle currency symbols
    # TODO: Handle missing prices
    
    return 0.0


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Parsed datetime
    """
    # TODO: Handle various date formats
    # TODO: Handle relative dates (e.g., "2 days ago")
    
    return datetime.now()


def normalize_text(text: str) -> str:
    """Normalize text for comparison and storage.
    
    Args:
        text: Raw text
        
    Returns:
        Normalized text
    """
    # TODO: Trim whitespace
    # TODO: Remove special characters
    # TODO: Handle Unicode normalization
    
    return text.strip().lower()
