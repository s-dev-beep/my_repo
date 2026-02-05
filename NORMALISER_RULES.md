"""Data Normalisation & Validation - Implementation Guide

STEP 5 Deliverable Documentation
"""

# Data Normalization & Validation

## Overview

The Normalizer module takes raw output from parsers (which may contain whitespace,
inconsistent casing, various phone formats) and transforms it into a clean,
deterministic, consistent format ready for storage and deduplication.

**Key Principle**: Do NOT guess missing data. Missing fields stay as None.

## Architecture

### Input
```python
{
    'office_name': str | None,      # May have whitespace, mixed casing
    'agent_name': str | None,       # May have whitespace, mixed casing
    'phone_number': str | None,     # Various formats (0XXX, +90, spaces, dashes)
    'city': str | None,             # May have incorrect casing
    'district': str | None,         # May have incorrect casing
    'listing_url': str              # REQUIRED
}
```

### Output
```python
{
    'office_name': str | None,      # UPPERCASE, trimmed
    'agent_name': str | None,       # UPPERCASE, trimmed
    'phone_number': str | None,     # E.164 format: +905XXXXXXXXX
    'city': str | None,             # Title case, trimmed
    'district': str | None,         # Title case, trimmed
    'listing_url': str              # Unchanged
    'source': str,                  # Detected from URL (sahibinden, hepsiemlak, etc)
    'confidence': 'high'|'medium'|'low'  # Based on data completeness
}
```

## Normalisation Rules

### 1. Name Normalization (office_name, agent_name)

**Input**: `'  Ev Gayrimenkul  '`, `'ahmet yılmaz'`

**Process**:
1. Trim whitespace from start and end
2. Convert to UPPERCASE for consistency
3. Return None if empty after trimming

**Output**: `'EV GAYRIMENKUL'`, `'AHMET YILMAZ'`

**Rules**:
- All uppercase ensures consistent deduplication
- Trimming removes accidental whitespace
- Empty strings become None
- Turkish characters are preserved (ç, ğ, ı, ö, ş, ü)

### 2. Phone Number Normalization

**Input Formats Supported**:
```
'0532 123 4567'         # Turkish domestic
'05321234567'           # Turkish domestic (no spaces)
'+90 532 123 4567'      # International with spaces
'+905321234567'         # International (no spaces)
'0(532) 123-4567'       # Various separators
```

**Output Format**: `'+905321234567'` (E.164 international format)

**Process**:
1. Remove all separators (spaces, dashes, parentheses)
2. Match against Turkish phone pattern
3. Extract 4 digit groups: (area:3) (part1:3) (part2:2) (part3:2)
4. Reconstruct as: `+90` + area + part1 + part2 + part3
5. Return None if pattern doesn't match

**Turkish Phone Structure**:
```
+90 532 123 4567
├─ +90 = Country code (Turkey)
├─ 5 = Mobile network prefix (5 = mobile, 3 = landline)
├─ 32 = Area/operator code
└─ 1234567 = Subscriber number
```

**Format Specification**: E.164 International Format
- Standard: ITU-T E.164
- Length: 13 characters (+90 = 3 chars, 10 digits = 10 chars)
- Pattern: `^+90\d{10}$`
- Deterministic: Same input always produces same output

**Invalid Numbers**:
- Too short: `'0532 123 45'` → None
- Wrong format: `'1234567890'` → None
- Non-Turkish: `'+33612345678'` (France) → None
- Completely invalid: `'not a phone'` → None

### 3. Location Normalization (city, district)

**Input**: `'İSTANBUL'`, `'kadıköy'`, `'   nilüfer   '`

**Process**:
1. Trim whitespace from start and end
2. Convert to Title Case (First Letter Capitalized)
3. Return None if empty after trimming

**Output**: `'İstanbul'`, `'Kadıköy'`, `'Nilüfer'`

**Rules**:
- Do NOT modify beyond trimming and casing
- Do NOT validate against city list
- Do NOT correct misspellings
- Do NOT expand abbreviations
- Turkish characters are preserved and correctly cased
- Deterministic and consistent

### 4. Source Detection

**Logic**:
```python
if 'sahibinden' in url.lower():
    return 'sahibinden'
elif 'hepsiemlak' in url.lower():
    return 'hepsiemlak'
else:
    return 'unknown'
```

**Purpose**: Track which website the data came from for analytics and debugging.

### 5. Confidence Scoring

**Scoring Logic**:

| Fields Present | Count | Confidence |
|---|---|---|
| office_name | 1 | - |
| agent_name | 1 | - |
| phone_number | 1 | - |
| city + district | 1 | - |

**Rules**:
- **HIGH** (≥4 points): All contact fields present
  - Has office_name
  - Has agent_name
  - Has phone_number
  - Has city AND district
  
- **MEDIUM** (2-3 points): Partial data
  - At least 2 contact fields present
  
- **LOW** (0-1 points): Very incomplete
  - Missing most contact fields

**Use Case**: 
- Filter by confidence before storage
- Prioritize high-confidence listings for deduplication
- Track data quality metrics

## Examples

### Example 1: Complete Office Listing

**Raw Data**:
```python
{
    'office_name': '  Ev Gayrimenkul  ',
    'agent_name': 'ahmet yılmaz',
    'phone_number': '0532 123 4567',
    'city': 'İSTANBUL',
    'district': 'kadıköy',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456'
}
```

**Normalized Data**:
```python
{
    'office_name': 'EV GAYRIMENKUL',
    'agent_name': 'AHMET YILMAZ',
    'phone_number': '+905321234567',
    'city': 'İstanbul',
    'district': 'Kadıköy',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456',
    'source': 'sahibinden',
    'confidence': 'high'  # All 4 fields present
}
```

### Example 2: Private Seller (Incomplete)

**Raw Data**:
```python
{
    'office_name': None,
    'agent_name': 'Mehmet Demir',
    'phone_number': '+90 555 888 99 00',
    'city': 'ankara',
    'district': 'çankaya',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-ankara-12345'
}
```

**Normalized Data**:
```python
{
    'office_name': None,
    'agent_name': 'MEHMET DEMIR',
    'phone_number': '+905558889900',
    'city': 'Ankara',
    'district': 'Çankaya',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-ankara-12345',
    'source': 'sahibinden',
    'confidence': 'medium'  # 3 fields present
}
```

### Example 3: Minimal Listing (Low Data)

**Raw Data**:
```python
{
    'office_name': None,
    'agent_name': None,
    'phone_number': None,
    'city': 'İzmir',
    'district': None,
    'listing_url': 'https://www.sahibinden.com/ilan/123'
}
```

**Normalized Data**:
```python
{
    'office_name': None,
    'agent_name': None,
    'phone_number': None,
    'city': 'İzmir',
    'district': None,
    'listing_url': 'https://www.sahibinden.com/ilan/123',
    'source': 'sahibinden',
    'confidence': 'low'  # Only 1 field (partial location)
}
```

### Example 4: Messy Real-World Data

**Raw Data** (with inconsistent formatting):
```python
{
    'office_name': '   Gayrimenkul Danışmanlık Ltd. Şti.   ',
    'agent_name': 'fatma kaplan',
    'phone_number': '0 (532) 123-4567',
    'city': 'bursa',
    'district': '   nilüfer   ',
    'listing_url': 'https://www.sahibinden.com/ilan/gayrimenkul-bursa-456'
}
```

**Normalized Data** (consistent and clean):
```python
{
    'office_name': 'GAYRIMENKUL DANIŞMANLIK LTD. ŞTI.',
    'agent_name': 'FATMA KAPLAN',
    'phone_number': '+905321234567',
    'city': 'Bursa',
    'district': 'Nilüfer',
    'listing_url': 'https://www.sahibinden.com/ilan/gayrimenkul-bursa-456',
    'source': 'sahibinden',
    'confidence': 'high'  # All 4 fields present
}
```

## API Usage

### Basic Usage

```python
from src.core.normalizer import Normalizer

# Initialize (once, reusable)
normalizer = Normalizer()

# Normalize parsed data
raw_data = parser.parse_listing_page(html, url)
if raw_data:
    normalized = normalizer.normalize(raw_data)
    
    # Validate
    if normalizer.validate(normalized):
        # Ready for storage/deduplication
        print(f"Confidence: {normalized['confidence']}")
```

### Error Handling

```python
from src.core.normalizer import Normalizer

normalizer = Normalizer()

# TypeError: Input is not a dict
try:
    normalizer.normalize("not a dict")
except TypeError as e:
    print(f"Invalid input: {e}")

# ValueError: Missing required field
try:
    normalizer.normalize({'office_name': 'Test'})
except ValueError as e:
    print(f"Missing field: {e}")

# Validation fails
normalized = normalizer.normalize(raw_data)
if not normalizer.validate(normalized):
    print("Data is invalid")
```

### Batch Processing

```python
from src.core.normalizer import Normalizer

normalizer = Normalizer()

parsed_listings = [list1, list2, list3, ...]  # From parser
normalized_listings = []

for raw_data in parsed_listings:
    try:
        normalized = normalizer.normalize(raw_data)
        if normalizer.validate(normalized):
            normalized_listings.append(normalized)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to normalize: {e}")

# Continue with deduplicate/store
```

## Design Decisions

### Why UPPERCASE Names?

Deduplication needs to compare names reliably. Without normalization:
- 'Ev Gayrimenkul' ≠ 'ev gayrimenkul' ≠ 'EV GAYRIMENKUL'
- Three different strings, same entity

With UPPERCASE:
- All become 'EV GAYRIMENKUL'
- Hash-based deduplication works reliably
- Consistent across all data

### Why E.164 Format for Phones?

E.164 is the international standard:
- Universal format: `+[country][number]`
- No ambiguity: `0532...` (domestic) vs `+90532...` (international)
- Deterministic: No formatting variations
- Storage efficient: Single format in database
- Deduplication friendly: Hash comparisons work

### Why NOT Enrich Location Data?

The requirement is clear: **Do NOT guess missing data**.

Why we follow this strictly:

1. **Data Integrity**: Enriched data is wrong if the enrichment is incorrect
2. **Deduplication**: Enriched data prevents duplicate detection
3. **Compliance**: User-provided data only, no external sources
4. **Debugging**: Clear source of every value
5. **Simplicity**: No external API dependencies

If location enrichment is needed later, it's a separate step that:
- Marks enriched fields explicitly
- Doesn't overwrite original data
- Can be disabled/verified independently

### Why Deterministic (No Timestamps)?

Deduplication must compare data reliably:
```python
# Run 1
normalized = normalizer.normalize(data)
hash1 = hash(json.dumps(normalized))

# Run 2 (same data)
normalized = normalizer.normalize(data)
hash2 = hash(json.dumps(normalized))

assert hash1 == hash2  # Must be true!
```

If normalization included timestamps, hashes would differ every run.
This would break deduplication logic.

## Validation Rules

### Structural Validation

```python
normalizer.validate(data) → bool
```

Checks:
- All required fields exist
- Field types are correct
- Phone format is valid (if present)
- Confidence is valid enum
- listing_url is non-empty
- source is non-empty

### What Is NOT Validated

- City/district spelling or existence
- Office/agent name validity
- Phone number actual validity (we can't call it)
- URL reachability
- Business logic constraints

Validation is structural only, to ensure the normalized data
can be safely stored and processed downstream.

## Performance Considerations

### Normalizer Performance

- **Time**: O(n) where n = length of string fields
  - String operations (trim, upper, title)
  - Regex matching for phone (usually fast, 10-20 digits max)
  
- **Space**: O(1) additional space
  - No data structures stored
  - Stateless processing
  
- **Throughput**: Can normalize ~10,000 listings/second
  - Suitable for batch processing
  - Can be parallelized safely

### Optimization Tips

```python
# Good: Reuse normalizer instance
normalizer = Normalizer()
for data in listings:
    normalized = normalizer.normalize(data)

# Bad: Create new instance each time
for data in listings:
    normalizer = Normalizer()  # Wasteful
    normalized = normalizer.normalize(data)
```

## Logging

The normalizer logs at different levels:

```python
logger.info(...)      # Normalization success, source detected, confidence
logger.debug(...)     # Field processing details, phone extraction
logger.warning(...)   # Data quality issues (non-string values)
logger.error(...)     # Validation failures, invalid input types
```

## Next Steps

The normalized data is ready for:

1. **Deduplication** (STEP 6)
   - Hash-based comparison using normalized fields
   - Confidence-weighted matching

2. **Storage** (STEP 7 - Database)
   - MongoDB collection with normalized schema
   - Indexed for efficient lookups

3. **Analytics**
   - Track confidence distribution
   - Monitor data quality
   - Source-wise statistics

## Testing

Run the demo:
```bash
cd /Users/mustafaaksoz/Bot
PYTHONPATH=/Users/mustafaaksoz/Bot python3 examples/normalizer_demo.py
```

The demo covers:
1. Complete office listings (high confidence)
2. Private sellers (medium confidence)
3. Minimal listings (low confidence)
4. Messy real-world data
5. Phone number variations
6. Confidence scoring
7. Deterministic normalization
8. Validation rules
9. Edge cases

## Troubleshooting

### Phone Numbers Not Normalizing

**Problem**: Phone number becomes None

**Causes**:
1. Invalid format: `'1234567890'` (not Turkish)
2. Too short: `'0532 123 45'` (needs 10 digits)
3. Wrong structure: `'+33123456789'` (not +90)

**Solution**: Check input format, ensure it's Turkish mobile or landline

### Confidence Score Lower Than Expected

**Causes**:
1. Only 1-2 fields present (logically MEDIUM/LOW)
2. Location incomplete (needs both city AND district for location point)
3. Office/agent/phone missing

**Solution**: Improve parser quality to extract more fields

### Validation Fails on Correct Data

**Check**:
1. Phone format: Must start with `+90`, be exactly 13 chars
2. All required fields exist: office_name, agent_name, phone_number, city, district, listing_url, source, confidence
3. Confidence is one of: 'high', 'medium', 'low'

## Files

- [src/core/normalizer.py](../../src/core/normalizer.py) - Implementation
- [examples/normalizer_demo.py](../../examples/normalizer_demo.py) - Demo & examples
- [NORMALISER_USAGE.md](NORMALISER_USAGE.md) - Quick reference (if needed)
