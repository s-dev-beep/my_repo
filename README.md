# Real Estate Crawler

A production-grade, config-driven web crawler for Turkish real estate sites (Sahibinden, Hepsiemlak).

## Features

- **Stability First**: Robust error handling, retry mechanisms, deduplication
- **Config-Driven**: YAML-based site configurations, environment variables
- **Async Architecture**: Concurrent crawling with controlled concurrency
- **Structured Logging**: Detailed logging for debugging and monitoring
- **MongoDB Integration**: Data persistence for analysis
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

# Run crawler
python -m src.cli
```

## Next Steps

- Implement core crawler logic
- Add MongoDB models
- Create site-specific adapters
- Add testing framework
