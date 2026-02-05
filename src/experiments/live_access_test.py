"""STEP 24: Live Access Test with Realistic Delays

Test 10 URLs with 10-15 second delays between requests to evaluate
if Sahibinden allows low-rate access without blocking.

NOT a crawl, NOT persistence. Just a feasibility test.
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.core.logger import setup_logger
from src.core.fetcher import Fetcher, FetchError, BlockedError

logger = setup_logger(__name__)


async def run_live_access_test(
    urls: List[str],
    delay_min: float = 10.0,
    delay_max: float = 15.0,
    report_path: str = "reports/step24_live_test.json",
) -> Dict[str, Any]:
    """Test live access to 10 URLs with realistic delays.

    Args:
        urls: List of URLs to test (use first 10)
        delay_min: Minimum delay between requests (seconds)
        delay_max: Maximum delay between requests (seconds)
        report_path: Path to save JSON report

    Returns:
        Report dict with results and summary
    """
    # Limit to 10 URLs
    test_urls = urls[:10]

    # Prepare report directory
    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    # Initialize fetcher with NO retries (single attempt per URL)
    fetcher = Fetcher(
        max_retries=0,
        requests_per_minute=6,  # 1 request per 10 seconds
        random_delay_min=0.0,
        random_delay_max=0.0,
        use_proxy=False,
    )

    results: List[Dict[str, Any]] = []
    blocked_at: Optional[int] = None
    total_duration = 0.0

    await fetcher.connect()
    try:
        for idx, url in enumerate(test_urls, 1):
            # Realistic delay between requests
            if idx > 1:
                delay = random.uniform(delay_min, delay_max)
                logger.info(f"Waiting {delay:.1f}s before request {idx}/{len(test_urls)}")
                await asyncio.sleep(delay)
                total_duration += delay

            start_time = datetime.now()
            status_code: Optional[int] = None
            error_reason: Optional[str] = None
            outcome = "success"

            try:
                logger.info(f"[{idx}/{len(test_urls)}] Fetching: {url}")
                html = await fetcher.fetch(url)
                status_code = getattr(fetcher, 'last_status_by_url', {}).get(url)
                logger.info(f"  ✓ Status {status_code}, {len(html)} bytes")

            except BlockedError as e:
                status_code = getattr(fetcher, 'last_status_by_url', {}).get(url)
                error_reason = "blocked_repeated"
                outcome = "blocked"
                blocked_at = idx
                logger.error(f"  ✗ Blocked (repeated): {e}")

            except FetchError as e:
                status_code = getattr(fetcher, 'last_status_by_url', {}).get(url)
                error_reason = str(e)
                outcome = "error"
                if status_code in {403, 429}:
                    outcome = "blocked"
                    blocked_at = idx
                logger.error(f"  ✗ Error: {e}")

            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()

            results.append({
                "index": idx,
                "url": url,
                "status_code": status_code,
                "outcome": outcome,
                "error_reason": error_reason,
                "request_duration_seconds": elapsed,
            })

            # Stop on blocking
            if blocked_at is not None:
                logger.warning(f"Blocked at request {idx}, stopping test")
                break

    finally:
        await fetcher.disconnect()

    # Compile report
    success_count = sum(1 for r in results if r["outcome"] == "success")
    blocked_count = sum(1 for r in results if r["outcome"] == "blocked")
    error_count = sum(1 for r in results if r["outcome"] == "error")

    report = {
        "run_id": f"step24_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "constraints": {
            "urls_tested": len(test_urls),
            "delay_min_seconds": delay_min,
            "delay_max_seconds": delay_max,
            "no_retries": True,
            "no_proxy": True,
        },
        "results": results,
        "summary": {
            "total_requests": len(results),
            "successful": success_count,
            "blocked": blocked_count,
            "errors": error_count,
            "blocked_at_request": blocked_at,
            "total_duration_seconds": total_duration,
            "success_rate": success_count / len(results) * 100 if results else 0.0,
        },
        "interpretation": _interpret_results(success_count, blocked_count, len(results)),
    }

    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    logger.info(f"Live access test report saved to: {report_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("STEP 24: LIVE ACCESS TEST - SUMMARY")
    print("=" * 80)
    print(f"Successful:         {success_count}/{len(results)}")
    print(f"Blocked:            {blocked_count}/{len(results)}")
    print(f"Errors:             {error_count}/{len(results)}")
    print(f"Success Rate:       {report['summary']['success_rate']:.1f}%")
    print(f"Total Duration:     {total_duration:.1f}s")
    if blocked_at:
        print(f"Blocked at:         Request {blocked_at}")
    print(f"Interpretation:     {report['interpretation']}")
    print("=" * 80)

    return report


def _interpret_results(success: int, blocked: int, total: int) -> str:
    """Interpret test results."""
    if total == 0:
        return "NO REQUESTS MADE"
    
    if blocked > 0 and success == 0:
        return "BLOCKED IMMEDIATELY - Need proxy or different approach"
    
    if success == total:
        return "SUCCESS - All requests went through! No blocking detected."
    
    if success >= total * 0.7:
        return "PARTIAL SUCCESS - Delays are working. Some requests blocked after pattern."
    
    if success > 0:
        return "LIMITED SUCCESS - Got some through. May need longer delays or proxy."
    
    return "FAILED - All requests blocked or errored"


if __name__ == "__main__":
    # Load URLs from pilot file
    pilot_file = Path("examples/pilot_urls.txt")
    if not pilot_file.exists():
        logger.error(f"Pilot URLs file not found: {pilot_file}")
        exit(1)

    with open(pilot_file) as f:
        urls = [line.strip() for line in f if line.strip()]

    # Run test
    report = asyncio.run(
        run_live_access_test(
            urls=urls,
            delay_min=10.0,
            delay_max=15.0,
            report_path="reports/step24_live_test.json",
        )
    )

    # Exit code based on results
    success_rate = report["summary"]["success_rate"]
    if success_rate >= 70:
        exit(0)  # Success
    elif report["summary"]["blocked"] > 0:
        exit(2)  # Blocked
    else:
        exit(3)  # Error
