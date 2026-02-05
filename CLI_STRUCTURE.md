# CLI Implementation Summary

## Architecture

The CLI is built using Python's `argparse` with a clean separation of concerns:

```
src/cli/
├── __init__.py        # Package marker
├── __main__.py        # Package entry point
├── index.py           # Main CLI setup and routing
└── commands.py        # Command handlers (stubs with logging)
```

## Command Structure

```
crawler
├── --log-level {debug,info,warning,error}  # Global flag
└── crawl                                    # Main command
    ├── full                                 # Full crawl subcommand
    │   ├── --domain {sahibinden,hepsiemlak} (required)
    │   └── --dry-run (optional)
    │
    ├── incremental                          # Incremental crawl subcommand
    │   ├── --domain {sahibinden,hepsiemlak} (required)
    │   └── --dry-run (optional)
    │
    ├── city                                 # City-specific crawl
    │   ├── --domain {sahibinden,hepsiemlak} (required)
    │   ├── --city TEXT (required)
    │   ├── --district TEXT (optional)
    │   └── --dry-run (optional)
    │
    └── resume                               # Resume interrupted crawl
        ├── --domain {sahibinden,hepsiemlak} (required)
        └── --dry-run (optional)
```

## Key Features

✅ **Clean Argument Parsing**: Uses argparse with subparsers for hierarchical command structure
✅ **Detailed Help**: Every command has clear help text and examples
✅ **Logging Integration**: Commands output to both console (colored) and file
✅ **Dry-Run Mode**: All commands support `--dry-run` for safe testing
✅ **Error Handling**: Invalid arguments caught by argparse with friendly messages
✅ **No Business Logic**: Command handlers only log intentions, no actual crawling

## Command Handlers (in src/cli/commands.py)

Each command maps to a stub function:
- `run_full_crawl(domain, dry_run)`
- `run_incremental_crawl(domain, dry_run)`
- `run_city_crawl(domain, city, district, dry_run)`
- `run_resume_crawl(domain, dry_run)`

**Handler Pattern**: Log what WOULD happen, then return exit code.

## Logging

Dual output:
1. **Console**: Colored output for visibility
2. **File**: Detailed logs with timestamps (logs/crawler.log)

## Example Usage

```bash
# Full crawl
python3 -m src.cli crawl full --domain=sahibinden

# Incremental with debug logging
python3 -m src.cli --log-level=debug crawl incremental --domain=hepsiemlak

# City-specific with optional district
python3 -m src.cli crawl city --domain=sahibinden --city=Istanbul --district=Besiktash

# Dry-run mode (no actual changes)
python3 -m src.cli crawl full --domain=sahibinden --dry-run

# Resume interrupted crawl
python3 -m src.cli crawl resume --domain=sahibinden

# Help
python3 -m src.cli --help
python3 -m src.cli crawl --help
python3 -m src.cli crawl full --help
```

## Exit Codes

- `0`: Success
- `1`: Error
- `2`: Invalid arguments
- `130`: Interrupted by user (Ctrl+C)

## Next Steps

These command handlers will be connected to actual crawling logic in future steps. For now, they:
- Parse and validate arguments
- Log the intended action
- Return success code

This allows testing the CLI interface without implementing business logic.
