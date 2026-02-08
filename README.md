# Real Estate Crawler (Light)

A lightweight crawler for Turkish real estate listings (Sahibinden, Hepsiemlak). It focuses on one job: collect listing contact/location info and append it to MongoDB and/or CSV.

## Features

- **Stability First**: Robust error handling, retry mechanisms
- **Config-Driven**: YAML-based site configurations, environment variables
- **Async Architecture**: Concurrent crawling with controlled concurrency
- **Structured Logging**: Detailed logging for debugging and monitoring
- **MongoDB Integration**: Append-only persistence (no overwrite, no dedup)
- **CSV Export**: Append normalized listings to CSV
- **Site Adapters**: Modular, site-specific parsers

## Tech Stack

- **Language**: Python 3.11+
- **Async**: asyncio
- **HTTP**: aiohttp
- **HTML Parsing**: BeautifulSoup4
- **Database**: MongoDB
- **Config**: YAML + .env

## Project Structure

```
src/
├── cli/           # CLI entry point
├── core/          # Core crawler components
├── adapters/      # Site-specific adapters
├── db/            # Database layer
└── utils/         # Utility functions

config/            # Configuration files
data/raw_html/     # Raw HTML storage
logs/              # Application logs
```

## Setup

```bash
# Install dependencies
pip install -e .

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Run crawler (append-only by default)
python -m src.cli crawl urls.txt

# Append-only + CSV export
python -m src.cli crawl urls.txt --mode append_only --output-csv exports/listings.csv

# CSV-only (no database)
python -m src.cli crawl urls.txt --mode append_only --output-csv exports/listings.csv --no-db
```

## One-command VPS bootstrap

On a fresh Ubuntu VPS:

```bash
curl -fsSL https://raw.githubusercontent.com/s-dev-beep/bot/main/scripts/bootstrap_vps.sh -o bootstrap_vps.sh
bash bootstrap_vps.sh
```

Optional overrides:

```bash
BOT_DIR=/home/sudeozyurt/Bot REPO_URL=https://github.com/s-dev-beep/bot.git bash bootstrap_vps.sh
```

## Docker (recommended for Ubuntu parity)

```bash
# Build image
docker build -t real-estate-crawler .

# Run
docker run --rm -it --env-file .env real-estate-crawler crawl /app/urls.txt
```

## Cache cleanup

Remove old cache/artifact files (default: older than 7 days):

python scripts/cleanup_cache.py

Dry run:

python scripts/cleanup_cache.py --dry-run --days 14

## Labeled cookies (VPS)

Cookie files are stored per label and overwritten on each warm-up to avoid growth.
Use labels like:

- sahibinden.com_real-estate
- sahibinden.com_araba
- hepsiemlak_real-estate
- arabam.com_araba

Warm-up script (interactive):

python scripts/warmup_cookies.py --url https://www.sahibinden.com --label sahibinden.com_real-estate --category real-estate

Non-interactive (wait N seconds):

python scripts/warmup_cookies.py --url https://www.sahibinden.com --label sahibinden.com_real-estate --category real-estate --wait-seconds 60

Docker (interactive, saves to ./data/cookies on host):

docker run --rm -it \
	-v $PWD/data:/app/data \
	mechul/real-estate-crawler:latest \
	python /app/scripts/warmup_cookies.py --url https://www.sahibinden.com --label sahibinden.com_real-estate --category real-estate
