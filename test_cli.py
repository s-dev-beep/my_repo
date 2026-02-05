#!/usr/bin/env python3
"""Test CLI basic functionality.

This script tests that the CLI can be invoked and shows help correctly.
"""

import subprocess
import sys

def test_cli_help():
    """Test that CLI help works."""
    print("Testing CLI help...")
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "--help"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0:
        print("✅ CLI help works")
        print(result.stdout)
        return True
    else:
        print("❌ CLI help failed")
        print(result.stderr)
        return False


def test_crawl_help():
    """Test that crawl command help works."""
    print("\nTesting crawl command help...")
    result = subprocess.run(
        ["python", "-m", "src.cli.main", "crawl", "--help"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0:
        print("✅ Crawl command help works")
        print(result.stdout)
        return True
    else:
        print("❌ Crawl command help failed")
        print(result.stderr)
        return False


def main():
    """Run CLI tests."""
    print("="*70)
    print("STEP 11 CLI - Basic Functionality Tests")
    print("="*70)
    print()
    
    tests = [
        test_cli_help,
        test_crawl_help,
    ]
    
    results = [test() for test in tests]
    
    print()
    print("="*70)
    if all(results):
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
