# HTML Parser Quick Reference

## Installation

```bash
pip install beautifulsoup4
```

## Basic Usage

```python
from src.adapters.sahibinden.parser import SahibindenParser

# Initialize parser (once, reusable)
parser = SahibindenParser()

# Parse a listing page
data = parser.parse_listing_page(
    html=raw_html_string,
    url="https://www.sahibinden.com/ilan/..."
)

# Access parsed data
if data:
    print(f"Office: {data['office_name']}")
    print(f"Agent: {data['agent_name']}")
    print(f"Phone: {data['phone_number']}")
    print(f"Location: {data['city']}, {data['district']}")
```

## Expected Output

```python
{
    'office_name': str | None,      # Real estate office name
    'agent_name': str | None,       # Agent's name
    'phone_number': str | None,     # Phone (limited - see docs)
    'city': str | None,             # From breadcrumb only
    'district': str | None,         # From breadcrumb only
    'listing_url': str              # Input URL
}
```

## Integration with Fetcher

```python
from src.core.fetcher import Fetcher
from src.adapters.sahibinden.parser import SahibindenParser

async def process_listing(url: str):
    # Fetch HTML
    fetcher = Fetcher()
    html = await fetcher.fetch(url)
    
    # Parse HTML
    parser = SahibindenParser()
    data = parser.parse_listing_page(html, url)
    
    return data
```

## Running the Demo

```bash
cd /Users/mustafaaksoz/Bot
PYTHONPATH=/Users/mustafaaksoz/Bot python3 examples/parser_demo.py
```

## Important Notes

1. **City/District**: Extracted ONLY from breadcrumb navigation
2. **Phone Numbers**: Limited support (static HTML only, no dynamic loading)
3. **All Fields Optional**: Parser returns partial data gracefully
4. **Stateless**: Same parser instance can parse multiple pages

## Common Patterns

### Check if data was parsed successfully

```python
data = parser.parse_listing_page(html, url)
if data is None:
    print("Failed to parse HTML")
else:
    # Process data (some fields may still be None)
    pass
```

### Handle missing fields

```python
data = parser.parse_listing_page(html, url)
if data:
    office = data.get('office_name') or 'Unknown'
    city = data.get('city') or 'Unknown'
    print(f"{office} in {city}")
```

### Batch processing

```python
parser = SahibindenParser()  # Create once

results = []
for html, url in listings:
    data = parser.parse_listing_page(html, url)
    if data:
        results.append(data)
```

## See Also

- [STEP4_SUMMARY.md](STEP4_SUMMARY.md) - Complete documentation
- [examples/parser_demo.py](examples/parser_demo.py) - Working examples
- [src/core/parser.py](src/core/parser.py) - Base parser interface
- [src/adapters/sahibinden/parser.py](src/adapters/sahibinden/parser.py) - Implementation
