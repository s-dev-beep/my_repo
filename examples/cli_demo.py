"""CLI usage examples.

STEP 11: Command Line Interface

This script demonstrates all CLI features.
Run with: python examples/cli_demo.py
"""

import subprocess
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def run_example(description: str, command: list[str], dry: bool = False):
    """Run a CLI example command."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{GREEN}Example: {description}{RESET}")
    print(f"{YELLOW}Command: {' '.join(command)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    if dry:
        print("[DRY RUN - command not executed]\n")
        return
    
    result = subprocess.run(command, capture_output=False)
    return result.returncode


def main():
    """Run all CLI examples."""
    print(f"\n{GREEN}╔═══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{GREEN}║         STEP 11: CLI USAGE EXAMPLES                               ║{RESET}")
    print(f"{GREEN}╚═══════════════════════════════════════════════════════════════════╝{RESET}\n")
    
    # Example 1: Basic crawl with dry_run mode
    run_example(
        "Basic crawl in dry_run mode (no DB writes)",
        [
            "python", "-m", "src.cli.main",
            "crawl", "examples/sample_urls_sahibinden.txt",
            "--mode", "dry_run",
        ],
        dry=True,
    )
    
    # Example 2: Safe run mode (high/medium confidence only)
    run_example(
        "Crawl with safe_run mode (high/medium confidence only)",
        [
            "python", "-m", "src.cli.main",
            "crawl", "examples/sample_urls_sahibinden.txt",
            "--mode", "safe_run",
        ],
        dry=True,
    )
    
    # Example 3: Full run with limit
    run_example(
        "Full crawl limited to first 5 URLs",
        [
            "python", "-m", "src.cli.main",
            "crawl", "examples/sample_urls_sahibinden.txt",
            "--mode", "full_run",
            "--limit", "5",
        ],
        dry=True,
    )
    
    # Example 4: Custom config and report path
    run_example(
        "Crawl with custom config and report path",
        [
            "python", "-m", "src.cli.main",
            "crawl", "examples/sample_urls_hepsiemlak.txt",
            "--config", "config/default.yaml",
            "--report", "reports/custom_report.json",
        ],
        dry=True,
    )
    
    # Example 5: Help
    run_example(
        "Show CLI help",
        [
            "python", "-m", "src.cli.main",
            "--help",
        ],
        dry=True,
    )
    
    # Example 6: Crawl command help
    run_example(
        "Show crawl command help",
        [
            "python", "-m", "src.cli.main",
            "crawl", "--help",
        ],
        dry=True,
    )
    
    print(f"\n{GREEN}╔═══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{GREEN}║  All examples shown (dry run). Remove dry=True to execute.       ║{RESET}")
    print(f"{GREEN}╚═══════════════════════════════════════════════════════════════════╝{RESET}\n")
    
    print(f"\n{BLUE}Quick reference:{RESET}")
    print(f"  • Basic:     python -m src.cli.main crawl urls.txt")
    print(f"  • Dry run:   python -m src.cli.main crawl urls.txt --mode dry_run")
    print(f"  • Safe run:  python -m src.cli.main crawl urls.txt --mode safe_run")
    print(f"  • Limited:   python -m src.cli.main crawl urls.txt --limit 10")
    print(f"  • Custom:    python -m src.cli.main crawl urls.txt --config custom.yaml")
    print(f"  • Help:      python -m src.cli.main --help\n")
    
    print(f"{YELLOW}Exit codes:{RESET}")
    print(f"  0 = Success")
    print(f"  1 = Invalid input (bad args, missing file, etc.)")
    print(f"  2 = Safety stop triggered")
    print(f"  3 = Runtime error (fetch/parse/DB error)\n")


if __name__ == "__main__":
    main()
