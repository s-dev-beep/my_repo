#!/usr/bin/env python3
"""Cleanup old cache/artifact files.

Deletes cache directories/files older than a given number of days.
Defaults to 7 days.
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Iterable

DEFAULT_TARGETS = [
    "data/chrome-remote",
    "data/playwright_profile",
    "data/cookies",
    "data/raw_html",
    "logs",
    "reports",
    "exports",
]


def iter_paths(targets: Iterable[str]) -> Iterable[Path]:
    for target in targets:
        path = Path(target)
        if path.exists():
            yield path


def is_older_than(path: Path, cutoff_ts: float) -> bool:
    try:
        return path.stat().st_mtime < cutoff_ts
    except FileNotFoundError:
        return False


def cleanup_path(path: Path, cutoff_ts: float, dry_run: bool) -> int:
    removed = 0
    if path.is_file():
        if is_older_than(path, cutoff_ts):
            if dry_run:
                print(f"DRY RUN: would remove file {path}")
            else:
                path.unlink(missing_ok=True)
                print(f"Removed file {path}")
            removed += 1
        return removed

    for root, dirs, files in os.walk(path, topdown=False):
        root_path = Path(root)
        for name in files:
            file_path = root_path / name
            if is_older_than(file_path, cutoff_ts):
                if dry_run:
                    print(f"DRY RUN: would remove file {file_path}")
                else:
                    file_path.unlink(missing_ok=True)
                    print(f"Removed file {file_path}")
                removed += 1
        for name in dirs:
            dir_path = root_path / name
            try:
                if not any(dir_path.iterdir()):
                    if dry_run:
                        print(f"DRY RUN: would remove empty dir {dir_path}")
                    else:
                        dir_path.rmdir()
                        print(f"Removed empty dir {dir_path}")
                    removed += 1
            except FileNotFoundError:
                continue
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Cleanup old cache/artifact files")
    parser.add_argument("--days", type=int, default=7, help="Remove files older than N days")
    parser.add_argument("--dry-run", action="store_true", help="List files without deleting")
    parser.add_argument(
        "--targets",
        nargs="*",
        default=DEFAULT_TARGETS,
        help="Override cleanup targets",
    )
    args = parser.parse_args()

    if args.days <= 0:
        raise ValueError("--days must be > 0")

    cutoff_ts = time.time() - (args.days * 24 * 60 * 60)

    total_removed = 0
    for path in iter_paths(args.targets):
        total_removed += cleanup_path(path, cutoff_ts, args.dry_run)

    print(f"Cleanup complete. Removed {total_removed} items.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
