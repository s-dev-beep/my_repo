"""Main package __main__ entry point."""

import asyncio
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.index import main


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
