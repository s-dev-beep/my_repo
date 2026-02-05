"""Deduplicator Quick Reference Guide

Quick usage guide for the deduplication module.
"""

# Deduplicator Quick Reference

## Installation

No additional packages needed - uses Python stdlib only.

## Basic Usage

```python
from src.core.deduplicator import Deduplicator

# Initialize (once, reusable)
dedup = Deduplicator()

# Check listing (by URL)
listing_data = {
    'listing_url': 'https://www.sahibinden.com/ilan/123',
    'office_name': 'EV GAYRIMENKUL',
    'phone_number': '+905321234567',
}

result = dedup.check_listing(listing_data)
print(f"New: {result.is_new}, Key: {result.dedupe_key}, Reason: {result.reason}")
# Output: New: True, Key: https://www.sahibinden.com/ilan/123, Reason: New listing URL: ...

# Register it
dedup.add_listing(listing_data['listing_url'])

# Check again
result = dedup.check_listing(listing_data)
print(result.is_new)  # False - now it's a duplicate
```

## Three Entity Types

### 1. Listing (by URL)

```python
# Check
result = dedup.check_listing({'listing_url': 'https://...'})
print(result.is_new)  # True or False

# Register
dedup.add_listing('https://...')
```

**Key**: URL only
**When Missing**: Cannot deduplicate → treated as new

### 2. Office (by name + phone)

```python
# Check
result = dedup.check_office({
    'office_name': 'EV GAYRIMENKUL',      # Required
    'phone_number': '+905321234567'       # Required (E.164 format)
})
print(result.is_new)  # True or False

# Register
dedup.add_office('EV GAYRIMENKUL', '+905321234567')
```

**Key**: office_name + phone_number
**When Missing**: If either field is missing → cannot deduplicate → treated as new
**Example**:
- Same office, different phone → NEW (different branch)
- Different office, same phone → NEW (different entity)
- Both same → DUPLICATE

### 3. Agent (by name + phone)

```python
# Check
result = dedup.check_agent({
    'agent_name': 'AHMET YILMAZ',         # Required
    'phone_number': '+905321234567'       # Required (E.164 format)
})
print(result.is_new)  # True or False

# Register
dedup.add_agent('AHMET YILMAZ', '+905321234567')
```

**Key**: agent_name + phone_number
**When Missing**: If either field is missing → cannot deduplicate → treated as new
**Example**:
- Same agent, different phone → NEW (probably different person)
- Different agent, same phone → NEW (definitely different person)
- Both same → DUPLICATE

## Batch Loading

```python
# Load multiple previously-seen entities at once
entities = [
    {
        'listing_url': 'https://...',
        'office_name': 'EV GAYRIMENKUL',
        'phone_number': '+905321234567',
        'agent_name': 'AHMET YILMAZ'
    },
    # more entities...
]

dedup.load_entities(entities)

# Now deduplicator knows about all these entities
stats = dedup.stats()
print(stats)  # {'listings': 3, 'offices': 2, 'agents': 2}
```

## Statistics & Management

```python
# Get statistics
stats = dedup.stats()
print(f"Listings: {stats['listings']}")
print(f"Offices: {stats['offices']}")
print(f"Agents: {stats['agents']}")

# Clear all entities (reset)
dedup.clear()
stats = dedup.stats()
print(stats)  # {'listings': 0, 'offices': 0, 'agents': 0}
```

## Typical Workflow

```python
from src.core.deduplicator import Deduplicator
from src.core.normalizer import Normalizer

# 1. Initialize
normalizer = Normalizer()
dedup = Deduplicator()

# 2. Load existing entities (optional)
existing_data = load_from_database()  # or file, cache, etc.
dedup.load_entities(existing_data)

# 3. Process new listings
for raw_listing in new_listings:
    # Normalize (STEP 5)
    normalized = normalizer.normalize(raw_listing)
    
    # Deduplicate (STEP 6)
    listing_result = dedup.check_listing(normalized)
    office_result = dedup.check_office(normalized)
    agent_result = dedup.check_agent(normalized)
    
    # Make decision
    if listing_result.is_new:
        print(f"New listing: {listing_result.reason}")
        dedup.add_listing(normalized['listing_url'])
    else:
        print(f"Duplicate listing: {listing_result.reason}")
    
    if office_result.is_new:
        print(f"New office: {office_result.reason}")
        if office_result.dedupe_key:
            parts = office_result.dedupe_key.split('#')
            dedup.add_office(parts[0], parts[1])
    else:
        print(f"Known office: {office_result.reason}")
    
    if agent_result.is_new:
        print(f"New agent: {agent_result.reason}")
        if agent_result.dedupe_key:
            parts = agent_result.dedupe_key.split('#')
            dedup.add_agent(parts[0], parts[1])
    else:
        print(f"Known agent: {agent_result.reason}")
    
    # Process based on decisions
    if listing_result.is_new:
        store_in_database(normalized)
    
    print()
```

## Output Schema

### DeduplicationResult

```python
result = dedup.check_listing(data)

# Access result fields
result.is_new       # bool: True if new, False if duplicate
result.dedupe_key   # str | None: The key used (e.g., URL, "NAME#PHONE")
result.reason       # str: Human-readable explanation
```

**Examples**:

**New Entity**:
```python
DeduplicationResult(
    is_new=True,
    dedupe_key='https://www.sahibinden.com/ilan/123',
    reason='New listing URL: https://www.sahibinden.com/ilan/123'
)
```

**Duplicate Entity**:
```python
DeduplicationResult(
    is_new=False,
    dedupe_key='https://www.sahibinden.com/ilan/123',
    reason='Listing URL already seen: https://www.sahibinden.com/ilan/123'
)
```

**Cannot Deduplicate**:
```python
DeduplicationResult(
    is_new=True,
    dedupe_key=None,
    reason='Cannot deduplicate office: missing office_name'
)
```

## Common Patterns

### Check if normalization succeeded

```python
dedup = Deduplicator()

data = {
    'listing_url': 'https://...',
    'office_name': 'EV GAYRIMENKUL',
    'phone_number': '+905321234567'
}

try:
    result = dedup.check_listing(data)
    print(f"✓ Listing check: is_new={result.is_new}")
except ValueError as e:
    print(f"✗ Invalid data: {e}")
```

### Filter by entity type

```python
dedup = Deduplicator()
normalized = normalizer.normalize(raw_data)

# Check all entity types
listing_result = dedup.check_listing(normalized)
office_result = dedup.check_office(normalized)
agent_result = dedup.check_agent(normalized)

# Process based on results
if listing_result.is_new:
    # New listing - might want to crawl details
    crawl_listing(normalized)
elif office_result.is_new:
    # Known listing, but new office
    check_office_details(normalized)
elif agent_result.is_new:
    # Known listing, known office, but new agent
    check_agent_details(normalized)
else:
    # Everything known - skip
    print("All entities already seen - skip")
```

### Batch processing with deduplication

```python
dedup = Deduplicator()
normalizer = Normalizer()

results = {
    'new_listings': [],
    'duplicates': [],
    'errors': []
}

for raw_data in parsed_listings:
    try:
        # Normalize
        normalized = normalizer.normalize(raw_data)
        
        # Check listing
        result = dedup.check_listing(normalized)
        if result.is_new:
            results['new_listings'].append(normalized)
            dedup.add_listing(normalized['listing_url'])
        else:
            results['duplicates'].append(normalized)
    
    except ValueError as e:
        results['errors'].append({'data': raw_data, 'error': str(e)})

# Summary
print(f"New: {len(results['new_listings'])}")
print(f"Duplicates: {len(results['duplicates'])}")
print(f"Errors: {len(results['errors'])}")
```

### Detailed logging

```python
dedup = Deduplicator()
normalized = normalizer.normalize(raw_data)

# Check all entity types
listing_result = dedup.check_listing(normalized)
office_result = dedup.check_office(normalized)
agent_result = dedup.check_agent(normalized)

# Log detailed results
import json
log_entry = {
    'url': normalized['listing_url'],
    'listing': {
        'is_new': listing_result.is_new,
        'key': listing_result.dedupe_key,
        'reason': listing_result.reason
    },
    'office': {
        'is_new': office_result.is_new,
        'key': office_result.dedupe_key,
        'reason': office_result.reason
    },
    'agent': {
        'is_new': agent_result.is_new,
        'key': agent_result.dedupe_key,
        'reason': agent_result.reason
    }
}

print(json.dumps(log_entry, indent=2))
```

## Key Principles

### 1. Deterministic
- No fuzzy matching
- No machine learning
- Same input → same output (always)

### 2. Conservative
- Missing fields → cannot deduplicate → treated as new
- Better to miss a duplicate than create a false positive
- Unknown is safer than wrong

### 3. No Side Effects
- check_* methods don't modify state
- Must explicitly call add_* to register entities
- Can check multiple times without registering

### 4. Strict Matching
- Case-sensitive (requires UPPERCASE from STEP 5)
- No whitespace trimming (done by STEP 5)
- No phone format changes (E.164 from STEP 5)
- This is why STEP 5 (Normalizer) is critical!

## Data Requirements from STEP 5

For deduplication to work correctly, input must be normalized:

```python
# ✓ CORRECT (from Normalizer)
data = {
    'office_name': 'EV GAYRIMENKUL',          # UPPERCASE
    'agent_name': 'AHMET YILMAZ',             # UPPERCASE
    'phone_number': '+905321234567',          # E.164 format
    'listing_url': 'https://www.sahibinden.com/ilan/123'
}

# ✗ WRONG (not normalized)
data = {
    'office_name': '  Ev Gayrimenkul  ',      # Not uppercase!
    'agent_name': 'ahmet yılmaz',             # Not uppercase!
    'phone_number': '0532 123 4567',          # Not E.164!
    'listing_url': 'https://www.sahibinden.com/ilan/123'
}

# The second example would NOT be detected as duplicate
# because the keys don't match exactly!
```

## Testing

```bash
# Run all tests
python3 test_deduplicator.py

# Run specific test class
python3 -m unittest test_deduplicator.TestListingDeduplication

# Run specific test method
python3 -m unittest test_deduplicator.TestListingDeduplication.test_new_listing

# Run with verbose output
python3 -m unittest test_deduplicator -v
```

## Common Issues & Solutions

### Issue: Everything is marked as NEW

**Cause**: Input is not normalized
**Solution**: Make sure data comes from Normalizer (STEP 5)

```python
# ✓ Correct
normalized = normalizer.normalize(raw_data)
result = dedup.check_listing(normalized)

# ✗ Wrong
raw_data = parser.parse(html)
result = dedup.check_listing(raw_data)  # Not normalized!
```

### Issue: Missing phone_number is treated as new office

**Cause**: Phone is required to deduplicate office
**Solution**: Only check office if both name and phone present

```python
data = {
    'office_name': 'EV GAYRIMENKUL',
    'phone_number': None  # Missing!
}

result = dedup.check_office(data)
print(result.is_new)  # True - cannot deduplicate without phone

# Solution: Check if phone exists first
if data.get('phone_number') and data.get('office_name'):
    result = dedup.check_office(data)
else:
    print("Cannot check office - missing required fields")
```

### Issue: Case sensitivity

**Cause**: Names must be UPPERCASE (from Normalizer)
**Solution**: Ensure data is normalized before checking

```python
# After Normalizer
data = {
    'office_name': 'EV GAYRIMENKUL',  # Already UPPERCASE
    'phone_number': '+905321234567'
}

result1 = dedup.check_office(data)
dedup.add_office('EV GAYRIMENKUL', '+905321234567')

# Later
data2 = {
    'office_name': 'ev gayrimenkul',  # NOT uppercase!
    'phone_number': '+905321234567'
}

result2 = dedup.check_office(data2)
print(result2.is_new)  # True - keys don't match!
```

## Performance Tips

### 1. Load Existing Entities Once
```python
# ✓ Good - load once
dedup = Deduplicator()
dedup.load_entities(existing_data)

for new_listing in new_listings:
    result = dedup.check_listing(new_listing)
    # ... process
```

### 2. Batch Load Instead of Individual Add
```python
# ✓ Better - batch load
dedup.load_entities([entity1, entity2, entity3, ...])

# ✗ Slower - individual adds
dedup.add_listing(entity1['listing_url'])
dedup.add_listing(entity2['listing_url'])
dedup.add_listing(entity3['listing_url'])
# ...
```

### 3. Check All Entity Types Once Per Listing
```python
# ✓ Good - check all once
result_listing = dedup.check_listing(data)
result_office = dedup.check_office(data)
result_agent = dedup.check_agent(data)

# ✗ Bad - repeated checks
for _ in range(10):
    dedup.check_listing(data)  # Redundant
```

## Next Steps (STEP 7+)

- **STEP 7**: Database Persistence
  - Store deduplication state in MongoDB
  - Query existing entities from database
  - Sync in-memory deduplicator with database

- **STEP 8**: Enhanced Resolution
  - Fuzzy matching for names
  - Phonetic similarity
  - Address-based deduplication
  - Machine learning models

## See Also

- [STEP6_SUMMARY.md](STEP6_SUMMARY.md) - Full documentation
- [examples/deduplicator_demo.py](examples/deduplicator_demo.py) - Interactive demo
- [test_deduplicator.py](test_deduplicator.py) - Test suite
- [src/core/deduplicator.py](src/core/deduplicator.py) - Source code
