"""CLI argument parser options.

STEP 11: Command Line Interface

This module defines argparse configuration for all CLI commands.
"""

import argparse
from typing import Any


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="bot",
        description="Production-grade real estate crawler CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Crawl URLs from file in dry-run mode
  bot crawl urls.txt --mode dry_run
  
  # Crawl with safe_run mode (high/medium confidence only)
  bot crawl urls.txt --mode safe_run
  
  # Crawl first 10 URLs in full_run mode
  bot crawl urls.txt --mode full_run --limit 10
  
  # Use custom config and report path
  bot crawl urls.txt --config custom.yaml --report results/report.json

    # Access surface experiment (STEP 22-A)
    bot surface_test --listing-url URL --agent-url URL --office-url URL --search-url URL

    # Browser feasibility test (STEP 23)
    bot browser_test --url URL --report reports/step23.json --screenshot reports/step23.png
  
Exit codes:
  0 = success
  1 = invalid input (bad args, missing file, etc.)
  2 = safety stop triggered
  3 = runtime error (fetch/parse/db error)
        """,
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # CRAWL command
    crawl_parser = subparsers.add_parser(
        "crawl",
        help="Crawl URLs from a file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Positional argument: URL file
    crawl_parser.add_argument(
        "url_file",
        help="Path to file containing URLs (one per line)",
    )
    
    # Optional: execution mode
    crawl_parser.add_argument(
        "--mode",
        choices=["dry_run", "safe_run", "full_run"],
        default=None,
        help=(
            "Execution mode (default: from config). "
            "dry_run: no DB writes | "
            "safe_run: high/medium confidence only | "
            "full_run: all data"
        ),
    )
    
    # Optional: limit number of URLs
    crawl_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Process only first N URLs (default: all)",
    )
    
    # Optional: custom config file
    crawl_parser.add_argument(
        "--config",
        default=None,
        metavar="PATH",
        help="Path to custom config YAML (default: config/default.yaml)",
    )
    
    # Optional: custom report path
    crawl_parser.add_argument(
        "--report",
        default=None,
        metavar="PATH",
        help="Path to save JSON report (default: reports/crawl_TIMESTAMP.json)",
    )

    # ACCESS SURFACE command (STEP 22-A)
    surface_parser = subparsers.add_parser(
        "surface_test",
        help="Run access surface experiment (STEP 22-A)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    surface_parser.add_argument(
        "--listing-url",
        required=True,
        help="Listing URL (single request)",
    )
    surface_parser.add_argument(
        "--agent-url",
        required=True,
        help="Agent profile URL (single request)",
    )
    surface_parser.add_argument(
        "--office-url",
        required=True,
        help="Office page URL (single request)",
    )
    surface_parser.add_argument(
        "--search-url",
        required=True,
        help="Search page URL (single request)",
    )
    surface_parser.add_argument(
        "--config",
        default=None,
        metavar="PATH",
        help="Path to custom config YAML (default: config/default.yaml)",
    )
    surface_parser.add_argument(
        "--report",
        default=None,
        metavar="PATH",
        help="Path to save JSON report (default: reports/step22a_TIMESTAMP.json)",
    )

    # BROWSER TEST command (STEP 23)
    browser_parser = subparsers.add_parser(
        "browser_test",
        help="Run browser-based feasibility test (STEP 23)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    browser_parser.add_argument(
        "--url",
        required=True,
        help="Single URL to test in a real browser",
    )
    browser_parser.add_argument(
        "--report",
        default=None,
        metavar="PATH",
        help="Path to save JSON report (default: reports/step23_TIMESTAMP.json)",
    )
    browser_parser.add_argument(
        "--screenshot",
        default=None,
        metavar="PATH",
        help="Path to save screenshot (default: reports/step23_TIMESTAMP.png)",
    )
    browser_parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chromium in headless mode",
    )
    
    return parser


def validate_args(args: Any) -> None:
    """Validate parsed arguments.
    
    Args:
        args: Parsed arguments from argparse
    
    Raises:
        ValueError: If arguments are invalid
    """
    # Check command exists
    if not args.command:
        raise ValueError("No command specified. Use --help for usage.")
    
    # Validate crawl command
    if args.command == "crawl":
        # Validate limit
        if args.limit is not None and args.limit <= 0:
            raise ValueError(f"--limit must be positive, got: {args.limit}")

    if args.command == "surface_test":
        for arg_name in ["listing_url", "agent_url", "office_url", "search_url"]:
            value = getattr(args, arg_name, None)
            if not value:
                raise ValueError(f"--{arg_name.replace('_', '-')} is required")

    if args.command == "browser_test":
        if not getattr(args, "url", None):
            raise ValueError("--url is required")
