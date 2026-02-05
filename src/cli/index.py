"""CLI entry point for the crawler."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.logger import setup_logger
from src.cli.commands import (
    run_full_crawl,
    run_incremental_crawl,
    run_city_crawl,
    run_resume_crawl,
)

logger = setup_logger(__name__)


def setup_argument_parser() -> argparse.ArgumentParser:
    """Setup and configure argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="crawler",
        description="Production-grade real estate crawler for Turkish property sites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full crawl for Sahibinden
  python -m src.cli crawl full --domain=sahibinden
  
  # Incremental crawl with debug logging
  python -m src.cli crawl incremental --domain=hepsiemlak --log-level=debug
  
  # City-specific crawl in Istanbul/Besiktash
  python -m src.cli crawl city --domain=sahibinden --city=Istanbul --district=Besiktash
  
  # Resume interrupted crawl
  python -m src.cli crawl resume --domain=sahibinden
  
  # Dry run mode
  python -m src.cli crawl full --domain=sahibinden --dry-run
        """,
    )
    
    # Global flags
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Set logging level (default: info)",
    )
    
    # Subparsers for main command
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
    )
    
    # CRAWL command with subcommands
    crawl_parser = subparsers.add_parser(
        "crawl",
        help="Crawling operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    crawl_subparsers = crawl_parser.add_subparsers(
        dest="crawl_mode",
        help="Crawl mode",
        required=True,
    )
    
    # --- FULL CRAWL ---
    full_parser = crawl_subparsers.add_parser(
        "full",
        help="Run a full crawl (reset and crawl all listings)",
    )
    full_parser.add_argument(
        "--domain",
        required=True,
        choices=["sahibinden", "hepsiemlak"],
        help="Domain to crawl (required)",
    )
    full_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in simulation mode without making changes",
    )
    
    # --- INCREMENTAL CRAWL ---
    incremental_parser = crawl_subparsers.add_parser(
        "incremental",
        help="Run an incremental crawl (only new listings)",
    )
    incremental_parser.add_argument(
        "--domain",
        required=True,
        choices=["sahibinden", "hepsiemlak"],
        help="Domain to crawl (required)",
    )
    incremental_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in simulation mode without making changes",
    )
    
    # --- CITY CRAWL ---
    city_parser = crawl_subparsers.add_parser(
        "city",
        help="Run a city-specific crawl",
    )
    city_parser.add_argument(
        "--domain",
        required=True,
        choices=["sahibinden", "hepsiemlak"],
        help="Domain to crawl (required)",
    )
    city_parser.add_argument(
        "--city",
        required=True,
        help="City name (e.g., Istanbul, Adana)",
    )
    city_parser.add_argument(
        "--district",
        help="District within city (optional)",
    )
    city_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in simulation mode without making changes",
    )
    
    # --- RESUME CRAWL ---
    resume_parser = crawl_subparsers.add_parser(
        "resume",
        help="Resume a previously interrupted crawl",
    )
    resume_parser.add_argument(
        "--domain",
        required=True,
        choices=["sahibinden", "hepsiemlak"],
        help="Domain to resume crawling (required)",
    )
    resume_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in simulation mode without making changes",
    )
    
    return parser


async def main():
    """Main entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Setup logger with specified level
    log_level = args.log_level.upper() if hasattr(args, "log_level") else "INFO"
    logger_instance = setup_logger(__name__, level=log_level)
    
    # If no command provided, show help
    if not hasattr(args, "command") or args.command is None:
        parser.print_help()
        return 0
    
    try:
        # Route to appropriate command handler
        if args.command == "crawl":
            if args.crawl_mode == "full":
                exit_code = await run_full_crawl(
                    domain=args.domain,
                    dry_run=args.dry_run,
                )
            elif args.crawl_mode == "incremental":
                exit_code = await run_incremental_crawl(
                    domain=args.domain,
                    dry_run=args.dry_run,
                )
            elif args.crawl_mode == "city":
                exit_code = await run_city_crawl(
                    domain=args.domain,
                    city=args.city,
                    district=args.district,
                    dry_run=args.dry_run,
                )
            elif args.crawl_mode == "resume":
                exit_code = await run_resume_crawl(
                    domain=args.domain,
                    dry_run=args.dry_run,
                )
            else:
                logger_instance.error(f"Unknown crawl mode: {args.crawl_mode}")
                return 1
        else:
            logger_instance.error(f"Unknown command: {args.command}")
            return 1
        
        return exit_code
        
    except KeyboardInterrupt:
        logger_instance.warning("Crawl interrupted by user")
        return 130
    except Exception as e:
        logger_instance.error(f"Crawler failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
