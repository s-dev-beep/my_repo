"""CSV exporter for normalized listings."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class ListingCsvExporter:
    """Append-only CSV exporter for normalized listings."""

    FIELDNAMES = [
        "listing_url",
        "source",
        "confidence",
        "office_name",
        "agent_name",
        "phone_number",
        "city",
        "district",
        "crawl_run_id",
        "exported_at",
    ]

    def __init__(self, output_path: str) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.output_path.open("a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.FIELDNAMES)
        if self.output_path.stat().st_size == 0:
            self._writer.writeheader()
            self._file.flush()

    def write(self, normalized_data: Dict[str, Any]) -> None:
        row = self._to_row(normalized_data)
        self._writer.writerow(row)
        self._file.flush()

    def close(self) -> None:
        if not self._file.closed:
            self._file.close()

    def _to_row(self, normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "listing_url": normalized_data.get("listing_url"),
            "source": normalized_data.get("source"),
            "confidence": normalized_data.get("confidence"),
            "office_name": normalized_data.get("office_name"),
            "agent_name": normalized_data.get("agent_name"),
            "phone_number": normalized_data.get("phone_number"),
            "city": normalized_data.get("city"),
            "district": normalized_data.get("district"),
            "crawl_run_id": normalized_data.get("crawl_run_id"),
            "exported_at": datetime.utcnow().isoformat(),
        }
