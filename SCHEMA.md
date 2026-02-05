# STEP 13: CANONICAL ENTITY MODEL & DATA CONTRACT
## Schema Definitions

**Date:** February 2, 2026  
**Purpose:** Define and harden the canonical data model for crawler persistence  
**Status:** Design & Validation (ZERO behavior changes)

---

## EXECUTIVE SUMMARY

This document formalizes the canonical schema for three core entities:
- **Listing** (property record)
- **Office** (real estate office)
- **Agent** (real estate agent)

It also defines:
- Deduplication keys (uniqueness rules)
- Phone number ownership (agent vs office)
- Metadata contract (audit trail, source tracking)
- Validation rules (constraint enforcement)

This schema is designed to support future automation safely and consistently.

---

## CANONICAL SCHEMAS

### 1. LISTING Entity

**Purpose:** Represents a single property listing on a site  
**Unique Key:** `listing_url` (primary identifier)  
**MongoDB Collection:** `listings`

```
Listing {
  # Unique Identifier
  listing_url: string (REQUIRED)
    - Full URL to the property listing
    - Cannot be null
    - Unique constraint enforced
    - Example: "https://www.sahibinden.com/kiralik-daire-istanbul-besiktas-1"
    - Used as primary deduplication key

  # Contact Information (extracted from listing page)
  office_name: string | null
    - Real estate office name
    - Normalized to UPPERCASE
    - Trimmed of whitespace
    - Example: "ETAP GAYRIMENKUL"
    - CAN be null (listing may have no office info)

  agent_name: string | null
    - Individual real estate agent name
    - Normalized to UPPERCASE
    - Trimmed of whitespace
    - Example: "AHMET KAYA"
    - CAN be null (listing may be by office only)

  phone_number: string | null
    - Contact phone number
    - Normalized to E.164 format: +90XXXXXXXXXX
    - CAN be null (contact info may be hidden)
    - Question: Does this phone belong to office or agent?
      - RULE: If extracted from listing, store with listing
      - RULE: Replicate to both office & agent (see ownership rules)

  # Location Information
  city: string | null
    - City name
    - Title case (first letter uppercase)
    - Trimmed of whitespace
    - Example: "Beşiktaş", "İstanbul"
    - CAN be null (location may be incomplete)

  district: string | null
    - District/neighborhood name
    - Title case
    - Trimmed of whitespace
    - Example: "Kadıköy", "Fatih"
    - CAN be null
    - Note: Currently shows category (e.g., "Kiralık Daire")

  # Source & Quality Information
  source: string | null
    - Site source
    - Valid values: "sahibinden", "hepsiemlak", others
    - Detected from URL during normalization
    - Example: "sahibinden"
    - CAN be null (for backwards compatibility)

  confidence: string | null
    - Data quality confidence level
    - Valid values: "high", "medium", "low"
    - Calculated by normalizer based on field completeness
    - high = all critical fields present (office, agent, phone, location)
    - medium = some fields present
    - low = minimal fields
    - CAN be null (for backwards compatibility)

  # Entity References
  office_id: string (ObjectId) | null
    - MongoDB reference to Office document
    - Populated during listing upsert (if office exists)
    - CAN be null (no office identified)
    - Allows querying office details without re-parsing

  agent_id: string (ObjectId) | null
    - MongoDB reference to Agent document
    - Populated during listing upsert (if agent exists)
    - CAN be null (no agent identified)
    - Allows querying agent details without re-parsing

  # Audit Trail
  _metadata: {
    run_id: string
      - Crawler run identifier
      - Allows grouping listings from same crawl
      - Example: "crawl_20260202_175806"

    source: string
      - Original data source (site name)
      - Example: "sahibinden"
      - May differ from "source" field (for consistency)

    confidence: string | null
      - Copy of confidence level
      - For easy filtering: db.listings.find({"_metadata.confidence": "high"})

    test: boolean (optional)
      - Flag indicating test/synthetic data
      - Used in STEP 12 validation
      - Allows filtering: db.listings.find({"_metadata.test": {$exists: false}})

    parser_version: string (optional, future)
      - Version of parser that processed this listing
      - Allows tracking parser changes over time

    timestamp: datetime (optional, future)
      - When this listing was first fetched
      - Separate from created_at (DB timestamp)
  }

  # Database Timestamps
  created_at: datetime
    - When listing was first inserted into DB
    - Set once, never updated
    - ISO 8601 format

  updated_at: datetime
    - When listing was last updated
    - Updated on every upsert
    - ISO 8601 format
    - Allows identifying recently-updated listings
}
```

**Constraints:**
- Primary key: `listing_url`
- Unique index: `{listing_url: 1}`
- Optional indexes:
  - `{source: 1, confidence: 1}` for filtering by source/quality
  - `{city: 1, district: 1}` for geographic queries
  - `{office_id: 1}` for office listings lookup
  - `{agent_id: 1}` for agent listings lookup
  - `{_metadata.run_id: 1}` for run-based queries

---

### 2. OFFICE Entity

**Purpose:** Represents a unique real estate office  
**Unique Key:** `name + phone_number` (composite key for deduplication)  
**MongoDB Collection:** `offices`

```
Office {
  # Identity
  name: string (REQUIRED for meaningful identity)
    - Office name
    - Normalized to UPPERCASE
    - Trimmed of whitespace
    - Example: "ETAP GAYRIMENKUL"
    - MUST NOT be null for proper deduplication

  phone_number: string | null
    - Office contact phone
    - Normalized to E.164 format: +90XXXXXXXXXX
    - IMPORTANT: Can be null (office may not have public phone)
    - When to fill:
      - If office appears in multiple listings with consistent phone
      - NOT always filled (lazy population)

  # Related Fields (future use)
  address: string | null
    - Office physical address
    - NOT currently extracted
    - Reserved for future parser enhancements

  city: string | null
    - Office location (city)
    - May differ from listing city
    - NOT currently extracted

  # Audit Trail
  _metadata: {
    source: string
      - Source site(s) where this office appears
      - Example: "sahibinden"
      - Can be array in future: ["sahibinden", "hepsiemlak"]

    first_seen: datetime (optional, future)
      - When office was first identified

    listing_count: int (optional, future)
      - Number of listings under this office
      - Useful for office popularity tracking

    test: boolean (optional)
      - Flag for test data (STEP 12 validation)
  }

  # Database Timestamps
  created_at: datetime
    - When office was first inserted
    - Set once, never updated

  updated_at: datetime
    - When office record was last modified
    - Updated when new listings reference it
}
```

**Constraints:**
- Primary key (implicit): `name + phone_number`
- Unique index: `{name: 1, phone_number: 1}` (sparse, handles null phone)
- Optional indexes:
  - `{city: 1}` for geographic lookups
  - `{_metadata.source: 1}` for source-based queries

**Deduplication Rule:**
```
If (office_name matches) AND (phone_number matches) THEN:
  Same office → UPSERT (update existing)
ELSE:
  Different office → INSERT (create new)

Special case: If phone_number is NULL
  - Cannot fully deduplicate
  - Still attempt to match on name
  - May result in duplicate offices with same name but no phone
  - LOG WARNING for manual review
```

---

### 3. AGENT Entity

**Purpose:** Represents a unique real estate agent  
**Unique Key:** `name + phone_number` (composite key for deduplication)  
**MongoDB Collection:** `agents`

```
Agent {
  # Identity
  name: string (REQUIRED for meaningful identity)
    - Agent full name
    - Normalized to UPPERCASE
    - Trimmed of whitespace
    - Example: "AHMET KAYA"
    - MUST NOT be null for proper deduplication

  phone_number: string | null
    - Agent contact phone
    - Normalized to E.164 format: +90XXXXXXXXXX
    - IMPORTANT: Can be null (agent may not have public phone)
    - When to fill:
      - If agent appears in multiple listings with consistent phone
      - NOT always filled (lazy population)

  # Related Fields (future use)
  email: string | null
    - Agent email address
    - NOT currently extracted

  office_id: string (ObjectId) | null
    - MongoDB reference to Office entity
    - NOT currently populated
    - Reserved for future: link agents to offices
    - Would allow queries like "all agents at this office"

  # Audit Trail
  _metadata: {
    source: string
      - Source site(s) where agent appears
      - Example: "sahibinden"

    first_seen: datetime (optional, future)
      - When agent was first identified

    listing_count: int (optional, future)
      - Number of listings handled by agent

    test: boolean (optional)
      - Flag for test data (STEP 12 validation)
  }

  # Database Timestamps
  created_at: datetime
    - When agent was first inserted

  updated_at: datetime
    - When agent record was last modified
}
```

**Constraints:**
- Primary key (implicit): `name + phone_number`
- Unique index: `{name: 1, phone_number: 1}` (sparse, handles null phone)
- Optional indexes:
  - `{_metadata.source: 1}` for source-based queries

**Deduplication Rule:**
```
If (agent_name matches) AND (phone_number matches) THEN:
  Same agent → UPSERT (update existing)
ELSE:
  Different agent → INSERT (create new)

Special case: If phone_number is NULL
  - Cannot fully deduplicate
  - Still attempt to match on name
  - May result in duplicate agents with same name but no phone
  - LOG WARNING for manual review
```

---

## METADATA CONTRACT

All entities include a `_metadata` field that captures audit and operational information.

### Standard _metadata Structure

```
_metadata: {
  # Operational Context
  run_id: string
    - Unique identifier for the crawler run
    - Format: "crawl_YYYYMMDD_HHMMSS" (from timestamp)
    - Allows grouping: db.listings.find({"_metadata.run_id": "crawl_20260202_175806"})
    - Supports run-based analysis and cleanup

  source: string
    - Data source (site name)
    - Valid values: "sahibinden", "hepsiemlak", etc.
    - Example: "sahibinden"
    - Enables multi-site analytics

  confidence: string | null (optional, for listings)
    - Convenience copy of listing confidence
    - Values: "high", "medium", "low"
    - Allows easy filtering: db.listings.find({"_metadata.confidence": "high"})

  test: boolean (optional)
    - Flag for test/synthetic data
    - Used in STEP 12: db.listings.find({"_metadata.test": true})
    - Allows filtering out test runs from production analysis
    - When true: data was from synthetic/fixture test

  # Future Extensions (reserved)
  parser_version: string (future)
    - Version of parser that processed this data
    - Allows tracking parser behavior over time
    - Format: "sahibinden@1.0.0"

  fetch_timestamp: datetime (future)
    - When the listing was fetched from the website
    - Different from DB created_at (insertion timestamp)
    - Enables "freshness" analysis

  quality_flags: array[string] (future)
    - Quality warnings/notes about this data
    - Example: ["dynamic_content", "missing_phone", "malformed_name"]
    - Allows categorizing data quality issues
}
```

---

## PHONE NUMBER OWNERSHIP RULES

**Problem:** A phone number in a listing can belong to an office, an agent, or both. How should it be stored?

### Rule 1: Single Source of Truth
```
Phone number is extracted ONCE during parsing.
It is stored in the Listing as-is.
```

### Rule 2: Phone Replication
```
When upsert_listing() is called:
  1. Store phone in Listing document
  2. If office_name exists → also store phone in Office document
  3. If agent_name exists → also store phone in Agent document

This creates redundancy but:
  ✓ Allows quick lookups: "what's the office phone?"
  ✓ Enables filtering: "offices with phone coverage"
  ✓ Simplifies downstream queries
```

### Rule 3: Deduplication
```
Phone number is part of the deduplication key:
  - Office dedup key: (office_name, phone_number)
  - Agent dedup key: (agent_name, phone_number)

Implication: Same phone with different names = different entities
  Example:
    ("ETAP GAYRIMENKUL", "+90 212 234 5678") → Office 1
    ("AHMET KAYA", "+90 212 234 5678") → Agent 1
  These are NOT duplicates. Both stored.

Justification:
  - Phone is truly shared (office → agent communication)
  - Name differentiates the entity type
  - Natural deduplication pattern
```

### Rule 4: NULL Phone Handling
```
If phone_number is NULL:
  - Office/Agent CAN still be created (on name alone)
  - Deduplication becomes name-only
  - Risk: Multiple offices named "ETAP GAYRIMENKUL" with no phone
  - LOG WARNING: "Cannot fully deduplicate office: no phone"
  - Recommendation: Manual review of NULL phone listings
```

### Rule 5: Phone Mutability
```
Phone numbers DO change:
  - Agent changes office → old office phone outdated
  - Office updates number → all agents affected
  
Current approach: NO phone number history
  - Upsert simply replaces phone
  - Old phone lost
  
Future enhancement: Phone history table
  - Track phone changes over time
  - Allows analyzing agent/office migrations
```

---

## DEDUPLICATION KEYS EXPLAINED

### Listing Deduplication Key
```
Primary Key: listing_url

Rationale:
  - URL is permanent identifier on site
  - Cannot change without new listing
  - Uniquely identifies property
  - Always non-null (required field)

Action: If same URL appears in two crawls
  → UPSERT (update listing, keep history in updated_at)
  → Prevents false duplicates

Example:
  Crawl 1: https://www.sahibinden.com/...?id=123
  Crawl 2: https://www.sahibinden.com/...?id=123
  Result: Single listing document (with updated_at refreshed)
```

### Office Deduplication Key
```
Composite Key: (office_name, phone_number)

Rationale:
  - Name alone insufficient (many "EMLAK" offices)
  - Phone is unique per office (in theory)
  - Combination provides strong identity
  - Handles office expansion: same name, new phone = new office

Action: If same office_name + phone appears in two listings
  → UPSERT (update office record)
  → Reflects continued activity from office

Edge case: NULL phone
  - Dedup on name alone
  - Risk of false duplicates
  - Logged as warning

Example:
  Listing 1: office="ETAP GAYRIMENKUL", phone="+90 212 234 5678"
  Listing 2: office="ETAP GAYRIMENKUL", phone="+90 212 234 5678"
  Result: Single office document (both listings reference it)
```

### Agent Deduplication Key
```
Composite Key: (agent_name, phone_number)

Rationale:
  - Name alone insufficient (common names like "AHMET KAYA")
  - Phone uniquely identifies person (in theory)
  - Combination provides strong identity
  - Handles agent moves: same name, new phone = different agent

Action: If same agent_name + phone appears in two listings
  → UPSERT (update agent record)
  → Reflects continued activity from agent

Edge case: NULL phone
  - Dedup on name alone
  - Risk of false duplicates (multiple "AHMET KAYA")
  - Logged as warning

Example:
  Listing 1: agent="AHMET KAYA", phone="+90 212 234 5678"
  Listing 2: agent="AHMET KAYA", phone="+90 212 234 5678"
  Result: Single agent document (both listings reference it)

  Listing 3: agent="AHMET KAYA", phone="+90 312 345 6789"
  Result: Different agent (different phone = different person)
```

---

## VALIDATION RULES

All entities must satisfy these constraints for valid persistence.

### Listing Validation
```
✓ listing_url
  - MUST be non-null
  - MUST be non-empty string
  - MUST match URL format (contains http://)
  - Action: REJECT if invalid

✓ office_name, agent_name
  - MAY be null
  - MUST be uppercase if non-null
  - MUST not exceed 255 characters
  - Action: WARN and normalize if not uppercase

✓ phone_number
  - MAY be null
  - IF non-null: MUST match E.164 format (+90XXXXXXXXXX)
  - MUST not exceed 15 characters (E.164 limit)
  - Action: WARN if not formatted, attempt to normalize

✓ city, district
  - MAY be null
  - MUST match title case if non-null (first letter uppercase)
  - MUST not exceed 100 characters
  - Action: WARN and normalize if not title case

✓ source
  - SHOULD be one of: "sahibinden", "hepsiemlak", etc.
  - MAY be null (for backwards compatibility)
  - Action: WARN if unknown source

✓ confidence
  - SHOULD be one of: "high", "medium", "low"
  - MAY be null (for backwards compatibility)
  - Action: WARN if invalid confidence
```

### Office Validation
```
✓ name
  - MUST be non-null (required for deduplication)
  - MUST be uppercase
  - MUST not exceed 255 characters
  - Action: REJECT if null or invalid

✓ phone_number
  - MAY be null
  - IF non-null: MUST match E.164 format
  - Action: WARN if not formatted

✓ _metadata
  - MUST have source field
  - source SHOULD be known site name
  - Action: WARN if source missing/unknown
```

### Agent Validation
```
✓ name
  - MUST be non-null (required for deduplication)
  - MUST be uppercase
  - MUST not exceed 255 characters
  - Action: REJECT if null or invalid

✓ phone_number
  - MAY be null
  - IF non-null: MUST match E.164 format
  - Action: WARN if not formatted

✓ _metadata
  - MUST have source field
  - source SHOULD be known site name
  - Action: WARN if source missing/unknown
```

---

## IMPLEMENTATION NOTES

### Current State (STEP 12)
The STEP 12 validation test confirmed:
- ✓ Listings stored with all required fields
- ✓ Offices created from listings (name + phone)
- ✓ Agents created from listings (name + phone)
- ✓ Metadata properly tracked (run_id, source, test flags)
- ✓ Deduplication working (7 offices for 8 listings as expected)

### Changes Required (STEP 13)
1. **Hardening:** Make schema validation explicit
2. **Consistency:** Ensure all new upserts follow schema
3. **Logging:** Add validation warnings for edge cases
4. **Documentation:** This file serves as reference

### No Changes Required To
- ✓ Parser logic (ZERO changes)
- ✓ Fetcher logic (ZERO changes)
- ✓ Normalizer logic (ZERO changes)
- ✓ Crawler orchestration (ZERO changes)
- ✓ Data persistence (already compliant)

---

## DESIGN DECISIONS & RATIONALE

### Decision 1: Phone at Multiple Levels
**Q:** Why store phone in Listing, Office, AND Agent?

**A:** Redundancy for query efficiency
- Listing phone: "What's the contact for this specific property?"
- Office phone: "What's the main office number?"
- Agent phone: "What's this agent's direct number?"
Without redundancy, every query requires joins.

**Trade-off:**
- Con: Potential inconsistency (agent phone updated but listing not)
- Pro: Query simplicity and speed (no joins needed)
- Mitigation: Update logic ensures consistency during upsert

---

### Decision 2: Composite Dedup Keys
**Q:** Why (name, phone) instead of just phone?

**A:** Phone alone is insufficient
- Multiple people can share a phone (office reception)
- Same person may have multiple phones (office, cell, moved offices)
- Name + phone provides strong identity

---

### Decision 3: NULL Phone Allowed
**Q:** Why allow NULL phone if dedup depends on it?

**A:** Real-world data reality
- Some offices don't publish phone (privacy, policy)
- Some agents don't have public contact
- Rejecting these would lose data
- Solution: Warn on NULL dedup, flag for manual review

---

### Decision 4: String Confidence (not numeric)
**Q:** Why "high"/"medium"/"low" instead of 0.0-1.0?

**A:** Categorical vs continuous
- Categorical: Human-readable, consistent bucketing
- Continuous: Allows finer gradations
- Choice: Categorical is simpler now, can extend to numeric in future
- Implementation: Normalizer produces string, repositories can map to numeric if needed

---

### Decision 5: Separate City/District/Source/Confidence in Listing
**Q:** Why duplicate these in _metadata?

**A:** Filtering efficiency
- MongoDB must evaluate entire document for $match
- Storing at top level: index works
- Storing only in _metadata: slower queries
- Trade-off: Slight redundancy for query speed

---

## MIGRATION PATH (If Schema Changes)

This schema is FROZEN for STEP 13-14.

If future changes needed:
1. **Add new fields as OPTIONAL** (append-only)
2. **Never remove fields** (backwards compatibility)
3. **Rename via versioning** (create v2 field, keep v1 for legacy)
4. **Backfill gradually** (not all at once)

Example:
```
If we need: phone_type (office_phone vs agent_phone vs shared)
  - Add new field: phone_type: "shared" | "office" | "agent" | null
  - Make optional (null means unknown)
  - Backfill over time
  - Never delete old phone field
```

---

## VALIDATION CHECKLIST

- [ ] Listing schema matches MongoDB schema
- [ ] Office schema matches MongoDB schema
- [ ] Agent schema matches MongoDB schema
- [ ] Deduplication keys are explicit and tested
- [ ] Phone ownership rules documented
- [ ] Metadata contract defined
- [ ] Validation rules specified
- [ ] All fields documented with examples
- [ ] Edge cases (NULL fields) documented
- [ ] No parser/fetcher logic changes
- [ ] No crawler behavior changes

---

## CONCLUSION

This schema formalizes the data contract that STEP 12 validated.

**Key Points:**
1. **Three entities:** Listing, Office, Agent
2. **Dedup keys:** URL for listings, (name+phone) for office/agent
3. **Phone ownership:** Replicated across all three (for query efficiency)
4. **Metadata contract:** Tracks source, run, confidence, test flags
5. **Validation rules:** Explicit constraints on all fields
6. **NULL handling:** Allowed but logged (enables real-world data)

This schema is stable and suitable for automation in STEP 14+.

---

**Status:** ✅ Design Complete  
**Ready for:** STEP 14 (Validation Automation)  
**Frozen until:** Next major crawler version
