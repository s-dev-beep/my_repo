"""CLI main entrypoint.

STEP 11: Command Line Interface

This is the primary entrypoint for the CLI.
Usage: python -m src.cli.main [command] [args]
Or via setuptools entry point: bot [command] [args]
"""

import sys
import asyncio

from src.core.logger import setup_logger
from src.cli.options import create_parser, validate_args
from src.cli.commands import crawl_command, access_surface_command, browser_feasibility_command

logger = setup_logger(__name__)


async def main() -> int:
    """Main CLI entrypoint.
    
    Returns:
        Exit code
    """
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # If no command, show help
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        # Validate arguments
        validate_args(args)
    except ValueError as e:
        logger.error(f"Invalid arguments: {e}")
        parser.print_help()
        return 1
    
    # Route to command handler
    if args.command == "crawl":
        return await crawl_command(
            url_file=args.url_file,
            mode=args.mode,
            limit=args.limit,
            config_path=args.config,
            report_path=args.report,
        )
    elif args.command == "surface_test":
        return await access_surface_command(
            listing_url=args.listing_url,
            agent_url=args.agent_url,
            office_url=args.office_url,
            search_url=args.search_url,
            config_path=args.config,
            report_path=args.report,
        )
    elif args.command == "browser_test":
        return await browser_feasibility_command(
            url=args.url,
            report_path=args.report,
            screenshot_path=args.screenshot,
            headless=args.headless,
        )
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1


def cli_main():
    """Synchronous wrapper for setuptools entry point."""
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


if __name__ == "__main__":
    cli_main()
