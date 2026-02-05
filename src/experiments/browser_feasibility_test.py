"""STEP 23: Browser-Based Access Feasibility Test.

Goal:
- Test access via a real browser engine (Chromium).
- Exactly one URL, no retries, no scrolling.
- Extract only: phone number + office name.
- Log-only (no identity graph persistence).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from src.core.logger import setup_logger

logger = setup_logger(__name__)

BLOCK_STATUSES = {403, 429}


PHONE_REGEX = re.compile(
    r"(\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2})|"  # +90 5xx xxx xx xx
    r"(0\s?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2})"     # 05xx xxx xx xx
)

OFFICE_REGEX = re.compile(
    r"(?:Emlak|Gayrimenkul)\s+Ofisi\s*[:\-]?\s*"  # label
    r"([A-Za-zÇĞİÖŞÜçğıöşü0-9 .\-']{2,60})",
    re.IGNORECASE,
)


@dataclass
class BrowserTestResult:
    url: str
    status_code: Optional[int]
    rendered_title: Optional[str]
    phone_found: bool
    office_name: Optional[str]
    block_detected: bool
    screenshot_path: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "rendered_title": self.rendered_title,
            "phone_found": self.phone_found,
            "office_name": self.office_name,
            "block_detected": self.block_detected,
            "screenshot_path": self.screenshot_path,
        }


class BrowserFeasibilityTest:
    """Run a single-URL browser-based feasibility test."""

    def __init__(self, headed: bool = True) -> None:
        self.headed = headed

    def run(self, url: str, report_path: str, screenshot_path: str) -> Dict[str, Any]:
        """Execute the browser feasibility test.

        Args:
            url: Single URL to test
            report_path: JSON report output path
            screenshot_path: Screenshot output path

        Returns:
            Report dict
        """
        try:
            from playwright.sync_api import sync_playwright
            logger.info("Playwright loaded successfully")
        except ImportError as e:  # pragma: no cover - runtime dependency
            logger.error(f"Playwright not installed: {e}")
            logger.error("Install with: pip install playwright && playwright install chromium")
            raise RuntimeError(
                "Playwright is required. Install with: pip install playwright && playwright install chromium"
            ) from e

        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        screenshot_file = Path(screenshot_path)
        screenshot_file.parent.mkdir(parents=True, exist_ok=True)

        status_code: Optional[int] = None
        rendered_title: Optional[str] = None
        phone_found = False
        office_name: Optional[str] = None
        block_detected = False

        logger.info(f"Launching Chromium browser (headless={not self.headed})")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=not self.headed,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Stealth: hide automation signals
            page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => false})"
            )

            logger.info(f"Navigating to: {url}")
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if response is not None:
                status_code = response.status
                logger.info(f"Response status: {status_code}")
            else:
                logger.warning("No response object (page loaded via service worker?)")

            rendered_title = page.title()
            logger.info(f"Page title: {rendered_title}")

            # Extract only phone + office name (minimal parsing)
            text = page.inner_text("body")
            phone_found = bool(PHONE_REGEX.search(text))
            office_match = OFFICE_REGEX.search(text)
            office_name = office_match.group(1).strip() if office_match else None
            
            if phone_found:
                logger.info(f"✓ Phone found in page content")
            if office_name:
                logger.info(f"✓ Office found: {office_name}")

            # Block detection: status or obvious block text
            block_text = text.lower()
            block_detected = (
                status_code in BLOCK_STATUSES
                or "captcha" in block_text
                or "robot" in block_text
                or "erişim" in block_text
                or "blocked" in block_text
            )
            
            if block_detected:
                logger.warning("Block detected on page!")

            # Screenshot (no scrolling)
            logger.info(f"Taking screenshot: {screenshot_file}")
            page.screenshot(path=str(screenshot_file), full_page=False)

            context.close()
            browser.close()

        result = BrowserTestResult(
            url=url,
            status_code=status_code,
            rendered_title=rendered_title,
            phone_found=phone_found,
            office_name=office_name,
            block_detected=block_detected,
            screenshot_path=str(screenshot_file),
        )

        report = {
            "run_id": f"step23_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "constraints": {
                "single_url": True,
                "no_retries": True,
                "no_scrolling": True,
                "no_identity_persistence": True,
            },
            "result": result.to_dict(),
        }

        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2))
        logger.info(f"Browser feasibility report saved to: {report_file}")
        return report
