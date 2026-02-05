"""DEDUPLICATOR DESIGN & ARCHITECTURE

Visual diagrams and architecture documentation for the deduplication module.
"""

# Deduplicator Architecture & Design Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 4: Parser        STEP 5: Normalizer      STEP 6: Deduplicator    │
│  ┌──────────────┐      ┌──────────────┐       ┌──────────────┐         │
│  │   Raw HTML   │  →   │  Clean Dict  │   →   │  is_new?     │         │
│  │              │      │              │       │              │         │
│  │ {'office':   │      │ {'office':   │       │ ✓ NEW        │         │
│  │  '  foo  ',  │      │  'FOO',      │       │   or         │         │
│  │  'phone':    │      │  'phone':    │       │ ✗ DUPLICATE  │         │
│  │  '0532...'}  │      │  '+9053...'}  │       │              │         │
│  └──────────────┘      └──────────────┘       └──────────────┘         │
│                                                                         │
│         Input                 Process                  Output           │
│      (messy)              (deterministic)           (decision)          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Deduplicator Internal Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                       DEDUPLICATOR CLASS                               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  In-Memory Storage (Three Separate Sets)                              │
│  ┌────────────────────────────────────────────────────────────┐       │
│  │  self.listings: Set[str]                                   │       │
│  │    ├─ 'https://www.sahibinden.com/ilan/123'               │       │
│  │    ├─ 'https://www.sahibinden.com/ilan/456'               │       │
│  │    └─ 'https://www.hepsiemlak.com/ilan/789'               │       │
│  │                                                             │       │
│  │  self.offices: Set[Tuple[str, str]]                        │       │
│  │    ├─ ('EV GAYRIMENKUL', '+905321234567')                 │       │
│  │    └─ ('PREMIUM EMLAK', '+905321111111')                  │       │
│  │                                                             │       │
│  │  self.agents: Set[Tuple[str, str]]                         │       │
│  │    ├─ ('AHMET YILMAZ', '+905321234567')                   │       │
│  │    └─ ('MEHMET DEMIR', '+905558889900')                   │       │
│  └────────────────────────────────────────────────────────────┘       │
│                                                                        │
│  Methods                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ Listing Deduplication                                           │ │
│  │  • check_listing(data) → DeduplicationResult                    │ │
│  │  • add_listing(url)                                             │ │
│  │                                                                 │ │
│  │ Office Deduplication                                            │ │
│  │  • check_office(data) → DeduplicationResult                    │ │
│  │  • add_office(name, phone)                                     │ │
│  │                                                                 │ │
│  │ Agent Deduplication                                             │ │
│  │  • check_agent(data) → DeduplicationResult                     │ │
│  │  • add_agent(name, phone)                                      │ │
│  │                                                                 │ │
│  │ Bulk Operations                                                 │ │
│  │  • load_entities(list) - Load multiple entities at once        │ │
│  │  • stats() - Get current counts                                │ │
│  │  • clear() - Reset deduplicator                                │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Deduplication Decision Flow

### Listing Deduplication (by URL)

```
┌─────────────────────────────────────────────────────────────────┐
│  Input: Normalized Data                                         │
│  Check: check_listing(data)                                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
                   ┌─────────────────────────┐
                   │ Has listing_url?        │
                   └─────────────────────────┘
                         │                │
                        NO               YES
                        │                │
                        ▼                ▼
                   ┌─────────────┐  ┌────────────────┐
                   │ is_new=True │  │ URL in set?    │
                   │ (Cannot     │  └────────────────┘
                   │  dedupe)    │        │        │
                   └─────────────┘       NO      YES
                                         │        │
                                         ▼        ▼
                                    ┌────────┐  ┌──────────┐
                                    │is_new  │  │is_new    │
                                    │=True   │  │=False    │
                                    │(NEW)   │  │(DUPLICATE)
                                    └────────┘  └──────────┘

Examples:
  First URL                    → is_new = True ✓ NEW
  Same URL again               → is_new = False ✓ DUPLICATE
  Different URL                → is_new = True ✓ NEW
  Missing/empty URL            → is_new = True (warning) → NEW
```

### Office Deduplication (by name + phone)

```
┌──────────────────────────────────────────────────────────────────┐
│  Input: Normalized Data                                          │
│  Check: check_office(data)                                       │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
                   ┌──────────────────────────────┐
                   │ Has office_name AND          │
                   │ phone_number?                │
                   └──────────────────────────────┘
                        │                │
                       NO               YES
                        │                │
                        ▼                ▼
                   ┌──────────────┐  ┌─────────────────────────┐
                   │ is_new=True  │  │ (name, phone) in set?   │
                   │ (Cannot      │  └─────────────────────────┘
                   │  dedupe)     │              │         │
                   └──────────────┘             NO        YES
                                                │         │
                                                ▼         ▼
                                           ┌────────┐  ┌──────────┐
                                           │is_new  │  │is_new    │
                                           │=True   │  │=False    │
                                           │(NEW)   │  │(DUPLICATE)
                                           └────────┘  └──────────┘

Examples:
  Office + Phone (first)       → is_new = True ✓ NEW
  Same Office + Phone (again)  → is_new = False ✓ DUPLICATE
  Same Office, different Phone → is_new = True ✓ NEW
  Different Office, same Phone → is_new = True ✓ NEW
  Missing office_name          → is_new = True (warning) → NEW
  Missing phone_number         → is_new = True (warning) → NEW
```

### Agent Deduplication (by name + phone)

```
┌──────────────────────────────────────────────────────────────────┐
│  Input: Normalized Data                                          │
│  Check: check_agent(data)                                        │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
                   ┌──────────────────────────────┐
                   │ Has agent_name AND           │
                   │ phone_number?                │
                   └──────────────────────────────┘
                        │                │
                       NO               YES
                        │                │
                        ▼                ▼
                   ┌──────────────┐  ┌─────────────────────────┐
                   │ is_new=True  │  │ (name, phone) in set?   │
                   │ (Cannot      │  └─────────────────────────┘
                   │  dedupe)     │              │         │
                   └──────────────┘             NO        YES
                                                │         │
                                                ▼         ▼
                                           ┌────────┐  ┌──────────┐
                                           │is_new  │  │is_new    │
                                           │=True   │  │=False    │
                                           │(NEW)   │  │(DUPLICATE)
                                           └────────┘  └──────────┘

Examples:
  Agent + Phone (first)        → is_new = True ✓ NEW
  Same Agent + Phone (again)   → is_new = False ✓ DUPLICATE
  Same Agent, different Phone  → is_new = True ✓ NEW
  Different Agent, same Phone  → is_new = True ✓ NEW
  Missing agent_name           → is_new = True (warning) → NEW
  Missing phone_number         → is_new = True (warning) → NEW
```

## Comparison: Three Entity Types

```
┌─────────────┬────────────────────────────┬──────────────────────────────┐
│ Entity      │ Deduplication Key          │ Missing Key Behavior         │
├─────────────┼────────────────────────────┼──────────────────────────────┤
│ LISTING     │ listing_url                │ Missing → is_new = True      │
│             │                            │ (conservative)               │
│             │ Example:                   │                              │
│             │ 'https://www.../ilan/123'  │ Cannot deduplicate without   │
│             │                            │ URL, so treat as new entity  │
├─────────────┼────────────────────────────┼──────────────────────────────┤
│ OFFICE      │ office_name +              │ Missing either field →       │
│             │ phone_number               │ is_new = True               │
│             │                            │ (conservative)               │
│             │ Example:                   │                              │
│             │ 'EV GAYRIMENKUL' +         │ Cannot deduplicate without   │
│             │ '+905321234567'            │ both name AND phone, so      │
│             │                            │ treat as new entity          │
├─────────────┼────────────────────────────┼──────────────────────────────┤
│ AGENT       │ agent_name +               │ Missing either field →       │
│             │ phone_number               │ is_new = True               │
│             │ (conservative)             │                              │
│             │ Example:                   │ Cannot deduplicate without   │
│             │ 'AHMET YILMAZ' +           │ both name AND phone, so      │
│             │ '+905321234567'            │ treat as new entity          │
└─────────────┴────────────────────────────┴──────────────────────────────┘
```

## Example Processing Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                       PROCESSING A LISTING                            │
└────────────────────────────────────────────────────────────────────────┘

Input Raw Data (from Parser):
┌──────────────────────────────────────────────────────────────┐
│ {                                                            │
│   'office': '  Ev Gayrimenkul  ',       ← Messy formatting  │
│   'agent': 'ahmet yılmaz',              ← Mixed case         │
│   'phone': '0532 123 4567',             ← Multiple formats   │
│   'city': 'İSTANBUL',                                        │
│   'url': 'https://...'                                       │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
STEP 5: Normalizer cleans data
┌──────────────────────────────────────────────────────────────┐
│ {                                                            │
│   'office_name': 'EV GAYRIMENKUL',      ← UPPERCASE, trimmed │
│   'agent_name': 'AHMET YILMAZ',         ← UPPERCASE, trimmed │
│   'phone_number': '+905321234567',      ← E.164 format       │
│   'city': 'İstanbul',                   ← Title case         │
│   'listing_url': 'https://...',         ← Same              │
│   'source': 'sahibinden',               ← Added             │
│   'confidence': 'high'                  ← Added             │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
STEP 6: Deduplicator checks entities
        ┌────────────────────────────────────────────────────┐
        │ 1. Check Listing                                   │
        │    Key: 'https://...'                              │
        │    In set? NO → is_new = True ✓ NEW               │
        │    Action: Add to set                              │
        │                                                    │
        │ 2. Check Office                                    │
        │    Key: ('EV GAYRIMENKUL', '+905321234567')        │
        │    In set? NO → is_new = True ✓ NEW               │
        │    Action: Add to set                              │
        │                                                    │
        │ 3. Check Agent                                     │
        │    Key: ('AHMET YILMAZ', '+905321234567')          │
        │    In set? NO → is_new = True ✓ NEW               │
        │    Action: Add to set                              │
        └────────────────────────────────────────────────────┘
                         │
                         ▼
Output:
┌──────────────────────────────────────────────────────────────┐
│ {                                                            │
│   'listing': {                                               │
│     'is_new': True,                                          │
│     'dedupe_key': 'https://...',                             │
│     'reason': 'New listing URL: https://...'                 │
│   },                                                         │
│   'office': {                                                │
│     'is_new': True,                                          │
│     'dedupe_key': 'EV GAYRIMENKUL#+905321234567',            │
│     'reason': 'New office: EV GAYRIMENKUL @ +9053...'        │
│   },                                                         │
│   'agent': {                                                 │
│     'is_new': True,                                          │
│     'dedupe_key': 'AHMET YILMAZ#+905321234567',              │
│     'reason': 'New agent: AHMET YILMAZ @ +9053...'           │
│   }                                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Set-Based Storage (O(1) Lookup)

```
Why Sets?
┌─────────────────────────────────────────────────────────────┐
│ Array/List              │ Hash Set (used)                    │
├─────────────────────────┼────────────────────────────────────┤
│ Lookup: O(n) - slow     │ Lookup: O(1) avg - FAST ✓         │
│ Space: O(n)             │ Space: O(n)                        │
│ Add: O(1) to end        │ Add: O(1) avg ✓                    │
│ No duplicates: manual   │ No duplicates: automatic ✓         │
└─────────────────────────┴────────────────────────────────────┘

Result: Fast deduplication for millions of entities
```

### 2. Separate Sets per Entity Type

```
Why Separate?
┌──────────────────────────────────────────────────────────────┐
│ One mixed Set                 │ Three separate Sets           │
├───────────────────────────────┼───────────────────────────────┤
│ Mixed types = complex         │ Clear separation ✓            │
│ Type checking = overhead      │ Type-safe operations ✓        │
│ Unclear semantics             │ Clear semantics ✓             │
│ Hard to track statistics      │ Easy stats per type ✓         │
└───────────────────────────────┴───────────────────────────────┘

Result: Clear, maintainable, type-safe design
```

### 3. Deterministic Matching Only

```
Why Deterministic?
┌──────────────────────────────────────────────────────────────┐
│ Fuzzy Matching              │ Deterministic (used)          │
├─────────────────────────────┼──────────────────────────────┤
│ Pros: Catch variations      │ Pros: Predictable ✓          │
│ Cons: False positives       │ Cons: Need clean input ✓     │
│ Cons: Slow                  │ Cons: Handled by STEP 5 ✓    │
│ Cons: Non-repeatable        │ Cons: N/A ✓                  │
│ Cons: Hard to debug         │ Cons: Easy to debug ✓        │
└─────────────────────────────┴──────────────────────────────┘

Result: Clean input from STEP 5 + fast, deterministic matching
```

### 4. Conservative with Missing Data

```
Why Conservative?
┌────────────────────────────────────────────────────────────────┐
│ Scenario: Office has name but missing phone                    │
│                                                                │
│ Aggressive approach:                                           │
│  - "We can partially match on name"                            │
│  - Dedup on office_name only                                   │
│  - RISK: Wrong matches (John's office ≠ Jane's office)         │
│                                                                │
│ Conservative approach (used):                                  │
│  - "We can't safely deduplicate without both fields"           │
│  - Treat as new (is_new = True)                                │
│  - SAFE: No false positives ✓                                  │
│  - BENEFIT: Can be stored with medium/low confidence ✓         │
└────────────────────────────────────────────────────────────────┘

Result: Better to miss a duplicate than make false positive
```

## Deduplication Result Dataclass

```python
@dataclass
class DeduplicationResult:
    """Result of deduplication check."""
    
    is_new: bool
    # True if new entity, False if duplicate
    
    dedupe_key: Optional[str]
    # The key used for matching (e.g., URL, "NAME#PHONE")
    # None if could not deduplicate
    
    reason: str
    # Human-readable explanation
    # Examples:
    # - "New listing URL: https://..."
    # - "Listing URL already seen: https://..."
    # - "Cannot deduplicate listing: missing listing_url"
```

## Integration Points

```
STEP 5 Output
    ↓
    ├─→ office_name: str | None (UPPERCASE, trimmed)
    ├─→ agent_name: str | None (UPPERCASE, trimmed)
    ├─→ phone_number: str | None (E.164 format)
    ├─→ listing_url: str (unchanged)
    └─→ [other fields preserved]
    ↓
STEP 6 Deduplicator
    ↓
    ├─→ Listing check: By URL
    ├─→ Office check: By name + phone
    └─→ Agent check: By name + phone
    ↓
Decision Output
    ├─→ is_new: True/False
    ├─→ dedupe_key: str | None
    └─→ reason: str
    ↓
STEP 7+ (Future)
    ├─→ Database storage
    ├─→ Persistence
    └─→ Distributed systems
```

## Performance Characteristics

```
Operation          | Time Complexity | Space Complexity | Notes
─────────────────────────────────────────────────────────────────
check_listing()    | O(1) avg        | N/A              | Hash lookup
add_listing()      | O(1) avg        | N/A              | Set insertion
check_office()     | O(1) avg        | N/A              | Tuple hash
add_office()       | O(1) avg        | N/A              | Set insertion
check_agent()      | O(1) avg        | N/A              | Tuple hash
add_agent()        | O(1) avg        | N/A              | Set insertion
load_entities(n)   | O(n)            | O(n)             | n entities
stats()            | O(1)            | N/A              | Simple counts
clear()            | O(1)            | O(1)             | Set clearing

Space Usage:
- Per listing: ~50-100 bytes (URL hash)
- Per office: ~50-100 bytes (tuple hash)
- Per agent: ~50-100 bytes (tuple hash)
- For 1M entities: ~100 MB (acceptable for RAM)
```

## Scalability

```
Scenario                | Memory | Speed | Feasible?
────────────────────────────────────────────────────
10K entities            | 1 MB   | <1ms  | ✓ Yes
100K entities           | 10 MB  | <1ms  | ✓ Yes
1M entities             | 100 MB | <1ms  | ✓ Yes
10M entities            | 1 GB   | <1ms  | ✓ Yes
100M entities           | 10 GB  | <1ms  | ✗ Too much RAM

For distributed systems or 100M+ entities:
→ Use STEP 7+ with database persistence
→ Bloom filters for distributed deduplication
→ Sharding strategies
```

## Summary

The deduplicator is a simple, fast, and reliable system for:
- Detecting duplicate listings by URL
- Detecting duplicate offices by (name, phone) pair
- Detecting duplicate agents by (name, phone) pair
- Handling missing/incomplete data conservatively
- Maintaining in-memory state with O(1) lookups

It intentionally avoids:
- Fuzzy matching (deterministic only)
- Database operations (STEP 7)
- Machine learning (out of scope)
- Complex logic (simple and clear)
