# STEP 11: Command Line Interface (CLI)

## Overview
Production-ready CLI for running the crawler without writing Python code.

## Features
✅ Run crawler with URL lists from files  
✅ Three execution modes: `dry_run`, `safe_run`, `full_run`  
✅ Override config with CLI flags  
✅ Limit number of URLs to process  
✅ Custom report paths  
✅ Proper exit codes for automation  
✅ Auto-detect parser from URLs  

---

## Installation

The CLI is already available as part of the project. No additional installation needed.

---

## Usage

### Basic Command Structure
```bash
python -m src.cli.main crawl <url_file> [options]
```

### Quick Start
```bash
# Crawl URLs in dry-run mode (no DB writes)
python -m src.cli.main crawl examples/sample_urls_sahibinden.txt --mode dry_run

# Crawl in safe-run mode (high/medium confidence only)
python -m src.cli.main crawl examples/sample_urls_sahibinden.txt --mode safe_run

# Crawl in full-run mode (all data)
python -m src.cli.main crawl examples/sample_urls_sahibinden.txt --mode full_run
```

---

## Command Reference

### `crawl` Command

Crawl URLs from a text file.

**Syntax:**
```bash
python -m src.cli.main crawl <url_file> [options]
```

**Arguments:**
- `url_file`: Path to file containing URLs (one per line)

**Options:**
- `--mode {dry_run|safe_run|full_run}`: Execution mode (default: from config)
  - `dry_run`: Fetch and parse, but don't write to database
  - `safe_run`: Only persist high/medium confidence listings
  - `full_run`: Persist all valid listings
- `--limit N`: Process only first N URLs (default: all)
- `--config PATH`: Path to custom config YAML (default: config/default.yaml)
- `--report PATH`: Path to save JSON report (default: reports/crawl_TIMESTAMP.json)

**Examples:**
```bash
# Crawl with default settings
python -m src.cli.main crawl urls.txt

# Dry run (no DB writes)
python -m src.cli.main crawl urls.txt --mode dry_run

# Process only first 10 URLs
python -m src.cli.main crawl urls.txt --limit 10

# Use custom config
python -m src.cli.main crawl urls.txt --config custom.yaml

# Custom report path
python -m src.cli.main crawl urls.txt --report results/my_report.json

# Combine options
python -m src.cli.main crawl urls.txt --mode safe_run --limit 50 --report results.json
```

---

## URL File Format

Create a text file with one URL per line:

```text
# This is a comment
https://www.sahibinden.com/ilan/emlak-konut-satilik-listing-1
https://www.sahibinden.com/ilan/emlak-konut-satilik-listing-2
https://www.sahibinden.com/ilan/emlak-konut-satilik-listing-3

# Empty lines and comments are ignored
https://www.sahibinden.com/ilan/emlak-konut-satilik-listing-4
```

**Rules:**
- One URL per line
- Lines starting with `#` are comments
- Empty lines are ignored
- All URLs must be from the same domain (sahibinden.com or hepsiemlak.com)

---

## Execution Modes

### 1. `dry_run`
- **Purpose**: Test without side effects
- **Behavior**:
  - Fetches HTML
  - Parses and normalizes data
  - **Does NOT write to database**
  - Generates report with what *would* be inserted
- **Use case**: Validate URLs, test parser, preview results

### 2. `safe_run`
- **Purpose**: Only persist high-quality data
- **Behavior**:
  - Fetches, parses, normalizes
  - **Only persists HIGH and MEDIUM confidence listings**
  - Skips LOW confidence listings
  - Generates report
- **Use case**: Production runs where quality matters

### 3. `full_run`
- **Purpose**: Persist all valid data
- **Behavior**:
  - Fetches, parses, normalizes
  - **Persists ALL valid listings** (high, medium, low confidence)
  - Generates report
- **Use case**: Bulk imports, comprehensive crawls

---

## Exit Codes

The CLI returns specific exit codes for automation:

| Code | Meaning | Description |
|------|---------|-------------|
| `0` | Success | Crawl completed successfully |
| `1` | Invalid Input | Bad arguments, missing file, invalid config |
| `2` | Safety Stop | Safety threshold triggered (fetch failures, blocks, quality rejections) |
| `3` | Runtime Error | Unexpected error during crawl |

**Example (bash):**
```bash
python -m src.cli.main crawl urls.txt
if [ $? -eq 0 ]; then
    echo "Success!"
elif [ $? -eq 2 ]; then
    echo "Safety stop triggered - check report"
fi
```

---

## Configuration

### Default Config
By default, CLI uses `config/default.yaml`:

```yaml
crawler:
  run_mode: full_run
  safety:
    max_fetch_failure_rate: 0.3
    max_consecutive_blocks: 5
    max_quality_rejection_rate: 0.5
```

### Override with CLI Flag
```bash
# Use custom config
python -m src.cli.main crawl urls.txt --config my_config.yaml
```

### Override with --mode Flag
```bash
# CLI flag overrides config file
python -m src.cli.main crawl urls.txt --mode dry_run
```

**Precedence:** CLI flags > Custom config > Default config

---

## Report Generation

Every crawl generates a JSON report with:
- Run metadata (ID, timestamps, duration)
- Execution mode
- Statistics (fetched, parsed, inserted, updated, failed)
- Success records
- Failure records (with reasons)
- Quality rejections
- Safety stop reason (if triggered)

**Default path:** `reports/crawl_YYYYMMDD_HHMMSS.json`

**Custom path:**
```bash
python -m src.cli.main crawl urls.txt --report my_report.json
```

**Report structure:**
```json
{
  "run_id": "crawl_20260202_103045",
  "start_time": "2026-02-02T10:30:45.123456",
  "end_time": "2026-02-02T10:35:12.654321",
  "duration_seconds": 267.53,
  "run_mode": "full_run",
  "stop_reason": null,
  "parser_type": "sahibinden",
  "total_urls": 100,
  "stats": {
    "total": 100,
    "fetched": 95,
    "parsed": 90,
    "normalized": 85,
    "inserted": 80,
    "updated": 5,
    "failed": 10,
    "quality_rejected": 5
  },
  "successful": [...],
  "failures": [...],
  "quality_rejections": [...]
}
```

---

## Error Handling

### Invalid URL File
```bash
$ python -m src.cli.main crawl nonexistent.txt
ERROR: Failed to load URLs: URL file not found: nonexistent.txt
Exit code: 1
```

### Mixed Domains
```bash
$ python -m src.cli.main crawl mixed_urls.txt
ERROR: Failed to create parser: Mixed domains detected. Expected sahibinden.com, got: https://hepsiemlak.com/...
Exit code: 1
```

### Invalid Config
```bash
$ python -m src.cli.main crawl urls.txt --config bad.yaml
ERROR: Failed to load config: Config file not found: bad.yaml
Exit code: 1
```

### Safety Stop
```bash
$ python -m src.cli.main crawl urls.txt
WARNING: Crawl stopped early: Fetch failure rate (0.35) exceeded threshold (0.30)
Exit code: 2
```

---

## Examples

See complete examples in:
- `examples/cli_demo.py` - Demonstrates all CLI features
- `examples/sample_urls_sahibinden.txt` - Example URL file for sahibinden.com
- `examples/sample_urls_hepsiemlak.txt` - Example URL file for hepsiemlak.com

Run demo:
```bash
python examples/cli_demo.py
```

---

## Architecture

### File Structure
```
src/cli/
├── __init__.py       # Public API
├── __main__.py       # Module entry point (python -m src.cli.main)
├── main.py           # CLI entrypoint
├── commands.py       # Command handlers (crawl logic)
├── options.py        # Argparse configuration
└── loaders.py        # Load URLs, config, parser
```

### Design Principles
- **Zero modifications** to core crawler code
- **Pure orchestration** - CLI just calls existing Crawler
- **Config as source of truth** - CLI flags override when needed
- **Deterministic** - same inputs = same outputs
- **Explicit** - no magic, no surprises

### Flow
```
CLI Input
  ↓
Parse Args (options.py)
  ↓
Load URLs (loaders.py)
  ↓
Load Config (loaders.py)
  ↓
Detect Parser (loaders.py)
  ↓
Create Crawler (commands.py)
  ↓
Run Crawler (existing Crawler.run())
  ↓
Save Report
  ↓
Return Exit Code
```

---

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError`, run from project root:
```bash
cd /path/to/Bot
python -m src.cli.main crawl urls.txt
```

### Database Connection
Ensure `MONGO_URI` environment variable is set:
```bash
export MONGO_URI="mongodb://localhost:27017"
python -m src.cli.main crawl urls.txt
```

### Parser Errors
Ensure all URLs are from the same domain:
```bash
# ✅ Good - all sahibinden
https://www.sahibinden.com/ilan/1
https://www.sahibinden.com/ilan/2

# ❌ Bad - mixed domains
https://www.sahibinden.com/ilan/1
https://www.hepsiemlak.com/listing/1
```

---

## Future Enhancements (NOT IMPLEMENTED)

The following are NOT part of STEP 11 but could be added later:
- ❌ Interactive mode
- ❌ Progress bars
- ❌ Multi-domain support in single run
- ❌ Resume from checkpoint
- ❌ Parallel crawling
- ❌ Scheduling/cron integration

STEP 11 is intentionally minimal and boring.

---

## Summary

STEP 11 provides a **production-ready CLI** that:
- ✅ Allows running crawler without writing code
- ✅ Supports all three execution modes
- ✅ Provides proper exit codes for automation
- ✅ Generates comprehensive JSON reports
- ✅ Makes zero changes to existing crawler logic

**The CLI is pure orchestration.** All crawling logic remains in the core modules.
