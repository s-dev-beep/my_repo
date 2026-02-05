"""STEP 22-A: Access Surface Experiment.

Goal:
- Identify which Sahibinden surfaces are accessible with minimal footprint.
- One request per surface per run.
- No retries.
- Abort on first 403/429.
- No proxies.
- Use same identity sink & safety logic for listing surface (Crawler).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from src.core.logger import setup_logger
from src.core.crawler import Crawler
from src.core.reporting import Reporter
from src.adapters.sahibinden.parser import SahibindenParser
from src.core.fetcher import Fetcher, FetchError, BlockedError

logger = setup_logger(__name__)


BLOCK_STATUSES = {403, 429}


@dataclass
class SurfaceResult:
    surface_type: str
    url: str
    status_code: Optional[int]
    block_reason: Optional[str]
    outcome: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface_type": self.surface_type,
            "url": self.url,
            "status_code": self.status_code,
            "block_reason": self.block_reason,
            "outcome": self.outcome,
        }


class AccessSurfaceExperiment:
    """Run a controlled, low-footprint access surface experiment."""

    def __init__(
        self,
        mongo_uri: str,
        db_name: str = "real_estate_crawler",
        requests_per_minute: int = 3,
    ) -> None:
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.fetcher_config = {
            "max_retries": 0,
            "requests_per_minute": requests_per_minute,
            "random_delay_min": 0.0,
            "random_delay_max": 0.0,
            "use_proxy": False,
        }
        self.safety_config = {
            "max_fetch_failure_rate": 0.0,
            "max_consecutive_blocks": 1,
            "max_quality_rejection_rate": 1.0,
            "min_urls_before_checks": 1,
        }

    async def run(
        self,
        listing_url: str,
        agent_profile_url: str,
        office_url: str,
        search_url: str,
        report_path: str,
    ) -> Dict[str, Any]:
        """Execute the access surface experiment.

        Returns:
            Experiment report dict.
        """
        run_id = f"step22a_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)

        results: List[SurfaceResult] = []
        abort_reason: Optional[str] = None
        aborted_surface: Optional[str] = None

        # 1) Listing surface (uses full identity sink & safety logic)
        listing_result, listing_report_path = await self._run_listing_surface(
            listing_url, run_id
        )
        results.append(listing_result)

        if listing_result.status_code in BLOCK_STATUSES:
            abort_reason = f"blocked_{listing_result.status_code}"
            aborted_surface = listing_result.surface_type

        # 2) Other surfaces (single fetch each, no retries)
        if abort_reason is None:
            other_results = await self._run_other_surfaces(
                {
                    "agent_profile": agent_profile_url,
                    "office_page": office_url,
                    "search_page": search_url,
                }
            )
            results.extend(other_results)

            for result in other_results:
                if result.status_code in BLOCK_STATUSES:
                    abort_reason = f"blocked_{result.status_code}"
                    aborted_surface = result.surface_type
                    break

        # If aborted, mark remaining surfaces as skipped
        if abort_reason is not None:
            results = self._mark_skipped(results, aborted_surface)

        comparison = {
            result.surface_type: {
                "status_code": result.status_code,
                "block_reason": result.block_reason,
            }
            for result in results
        }

        report = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "rules": {
                "max_requests_per_surface": 1,
                "no_retries": True,
                "abort_on_first_403_429": True,
                "use_proxy": False,
                "requests_per_minute": self.fetcher_config["requests_per_minute"],
            },
            "surfaces": [result.to_dict() for result in results],
            "comparison": comparison,
            "summary": {
                "aborted": abort_reason is not None,
                "abort_reason": abort_reason,
                "aborted_surface": aborted_surface,
            },
            "listing_crawl_report": str(listing_report_path),
        }

        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2))
        logger.info(f"Access surface report saved to: {report_file}")
        return report

    async def _run_listing_surface(self, url: str, run_id: str) -> tuple[SurfaceResult, Path]:
        """Run listing surface test via full crawler pipeline."""
        reporter = Reporter(
            run_id=f"{run_id}_listing",
            parser_type="sahibinden",
            run_mode="safe_run",
        )

        crawler = Crawler(
            parser=SahibindenParser(),
            mongo_uri=self.mongo_uri,
            db_name=self.db_name,
            reporter=reporter,
            run_mode="safe_run",
            enable_quality_gates=True,
            fetcher_config=self.fetcher_config,
            safety_config=self.safety_config,
        )

        stats = await crawler.run([url])
        report = reporter.generate_report()
        listing_report_path = Path("reports") / f"{reporter.run_id}.json"
        listing_report_path.parent.mkdir(parents=True, exist_ok=True)
        report.save(listing_report_path)

        status_code = crawler.fetcher.get_last_status(url)  # type: ignore[attr-defined]
        block_reason = self._block_reason_from_status(status_code)
        outcome = self._outcome_from_status(status_code, stats.failed)

        return (
            SurfaceResult(
                surface_type="listing",
                url=url,
                status_code=status_code,
                block_reason=block_reason,
                outcome=outcome,
            ),
            listing_report_path,
        )

    async def _run_other_surfaces(self, surface_urls: Dict[str, str]) -> List[SurfaceResult]:
        """Fetch other surfaces with no retries and abort on first 403/429."""
        fetcher = Fetcher(**self.fetcher_config)
        results: List[SurfaceResult] = []

        await fetcher.connect()
        try:
            for surface_type, url in surface_urls.items():
                try:
                    await fetcher.fetch(url)
                    status_code = fetcher.get_last_status(url)  # type: ignore[attr-defined]
                    block_reason = self._block_reason_from_status(status_code)
                    outcome = self._outcome_from_status(status_code, 0)
                except BlockedError as e:
                    status_code = fetcher.get_last_status(url)  # type: ignore[attr-defined]
                    block_reason = "blocked_repeated"
                    outcome = "blocked"
                    logger.warning(f"Blocked on {surface_type}: {e}")
                except FetchError as e:
                    status_code = fetcher.get_last_status(url)  # type: ignore[attr-defined]
                    block_reason = self._block_reason_from_status(status_code) or str(e)
                    outcome = "blocked" if status_code in BLOCK_STATUSES else "error"
                    logger.warning(f"Fetch failed on {surface_type}: {e}")

                result = SurfaceResult(
                    surface_type=surface_type,
                    url=url,
                    status_code=status_code,
                    block_reason=block_reason,
                    outcome=outcome,
                )
                results.append(result)

                if status_code in BLOCK_STATUSES:
                    break
        finally:
            await fetcher.disconnect()

        return results

    @staticmethod
    def _block_reason_from_status(status_code: Optional[int]) -> Optional[str]:
        if status_code in BLOCK_STATUSES:
            return f"blocked_{status_code}"
        if status_code is None:
            return None
        if status_code >= 400:
            return f"http_{status_code}"
        return None

    @staticmethod
    def _outcome_from_status(status_code: Optional[int], failed_count: int) -> str:
        if status_code in BLOCK_STATUSES:
            return "blocked"
        if status_code is None and failed_count > 0:
            return "error"
        if status_code is not None and status_code >= 400:
            return "error"
        return "ok"

    @staticmethod
    def _mark_skipped(
        results: List[SurfaceResult],
        aborted_surface: Optional[str],
    ) -> List[SurfaceResult]:
        """Mark remaining surfaces as skipped after abort."""
        if aborted_surface is None:
            return results

        surface_order = ["listing", "agent_profile", "office_page", "search_page"]
        if aborted_surface not in surface_order:
            return results

        abort_index = surface_order.index(aborted_surface)
        existing = {r.surface_type for r in results}

        for surface in surface_order[abort_index + 1 :]:
            if surface not in existing:
                results.append(
                    SurfaceResult(
                        surface_type=surface,
                        url="",
                        status_code=None,
                        block_reason="skipped_due_to_abort",
                        outcome="skipped",
                    )
                )
        return results
