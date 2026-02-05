"""CLI package entry point.

STEP 11: Command Line Interface

Allows running CLI as a module: python -m src.cli
"""

from src.cli.main import cli_main

if __name__ == "__main__":
    cli_main()
