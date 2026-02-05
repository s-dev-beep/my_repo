# STEP 11 CLI - Quick Reference

## Installation
```bash
pip install -e .
```

## Basic Usage
```bash
# Show help
python -m src.cli.main --help
python -m src.cli.main crawl --help

# Crawl URLs from file
python -m src.cli.main crawl urls.txt

# With execution mode
python -m src.cli.main crawl urls.txt --mode dry_run
python -m src.cli.main crawl urls.txt --mode safe_run
python -m src.cli.main crawl urls.txt --mode full_run

# With limit
python -m src.cli.main crawl urls.txt --limit 10

# With custom config
python -m src.cli.main crawl urls.txt --config my_config.yaml

# With custom report path
python -m src.cli.main crawl urls.txt --report results/my_report.json

# Combine options
python -m src.cli.main crawl urls.txt --mode safe_run --limit 50 --report results.json
```

## URL File Format
```text
# Comments start with #
https://www.sahibinden.com/ilan/emlak-konut-satilik-listing-1
https://www.sahibinden.com/ilan/emlak-konut-satilik-listing-2

# Empty lines ignored
https://www.sahibinden.com/ilan/emlak-konut-satilik-listing-3
```

## Execution Modes
- `dry_run` - Fetch and parse, NO database writes
- `safe_run` - Only persist HIGH/MEDIUM confidence listings
- `full_run` - Persist ALL valid listings

## Exit Codes
- `0` = Success
- `1` = Invalid input
- `2` = Safety stop triggered
- `3` = Runtime error

## Examples
```bash
# Test without DB writes
python -m src.cli.main crawl examples/sample_urls_sahibinden.txt --mode dry_run

# Process first 5 URLs
python -m src.cli.main crawl my_urls.txt --mode dry_run --limit 5

# Production crawl
python -m src.cli.main crawl production_urls.txt --mode safe_run
```

## Check Exit Code (bash)
```bash
python -m src.cli.main crawl urls.txt
if [ $? -eq 0 ]; then
    echo "Success!"
elif [ $? -eq 2 ]; then
    echo "Safety stop - check report"
fi
```

## Files Created
- `src/cli/main.py` - Entrypoint
- `src/cli/commands.py` - Crawl logic
- `src/cli/options.py` - Argument parser
- `src/cli/loaders.py` - URL/config loaders
- `examples/cli_demo.py` - Usage demo
- `STEP11_CLI.md` - Full documentation

## See Also
- Full docs: `STEP11_CLI.md`
- Summary: `STEP11_SUMMARY.md`
- Demo: `python examples/cli_demo.py`
