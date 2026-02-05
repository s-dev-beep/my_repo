## STEP 19: Enrichment Queue - Quick Reference

### What It Does

Enrichment queue adds observations to existing phone identities from public sources (Hepsiemlak, Google Places) without modifying crawler or creating new phones.

---

### Key Classes

#### EnrichmentTask
```python
task = EnrichmentTask(
    phone_e164="+905551234567",
    current_confidence=0.7,
    missing_fields=["office_address", "office_phone"],
    sources_to_try=["hepsiemlak", "google_places"]
)
```

#### EnrichmentQueue
```python
queue = EnrichmentQueue(db, max_age_hours=24)

# Get phones needing enrichment
candidates = queue.get_candidates(limit=10)
# → [{"phone_e164": "+905551234567", "confidence_score": 0.7, ...}]

# Find which fields are missing
missing = queue.get_missing_fields("+905551234567")
# → ["office_address", "office_phone"]

# Mark phone as recently enriched
queue.mark_enriched("+905551234567")
```

#### EnrichmentRunner
```python
runner = EnrichmentRunner(db, run_mode="safe_run", google_api_key="...")

# Enrich a batch of phones
stats = await runner.enrich_batch(limit=10, timeout_seconds=30.0)
# → {
#     "total_phones": 10,
#     "successfully_enriched": 8,
#     "failed": 2,
#     "observations_added": 15,
#     "phones": {...}
# }

# Run continuous enrichment
await runner.continuous_enrich(
    batch_size=10,
    batch_interval_seconds=60.0,
    max_batches=None  # Run forever
)
```

#### IdentityGraphResolver
```python
resolver = IdentityGraphResolver(db)

# Add enrichment observation
result = resolver.add_enrichment_observation(
    phone_e164="+905551234567",
    field_name="office_address",
    value="123 Main St, Istanbul",
    source="google_places",
    timestamp=datetime.utcnow()
)
# → {
#     "phone_e164": "+905551234567",
#     "field_name": "office_address",
#     "evidence_id": "...",
#     "enrichment": {"field_enhanced": True}
# }
```

---

### Usage Patterns

#### Pattern 1: Single Phone Enrichment
```python
from src.enrichment import EnrichmentQueue
from src.identity import IdentityGraphResolver

queue = EnrichmentQueue(db)
resolver = IdentityGraphResolver(db)

phone = "+905551234567"
missing = queue.get_missing_fields(phone)

if "office_address" in missing:
    # Fetch from external source
    address = fetch_from_google_places(phone)
    
    # Add to graph
    resolver.add_enrichment_observation(
        phone_e164=phone,
        field_name="office_address",
        value=address,
        source="google_places"
    )
```

#### Pattern 2: Batch Enrichment
```python
import asyncio
from src.enrichment import EnrichmentRunner

async def enrich():
    runner = EnrichmentRunner(db, run_mode="safe_run")
    stats = await runner.enrich_batch(limit=10)
    print(f"Enriched {stats['successfully_enriched']} phones")

asyncio.run(enrich())
```

#### Pattern 3: Continuous Enrichment
```python
import asyncio
from src.enrichment import EnrichmentRunner

async def run_enrichment_service():
    runner = EnrichmentRunner(db, run_mode="safe_run")
    await runner.continuous_enrich(
        batch_size=10,
        batch_interval_seconds=60.0  # New batch every minute
    )

# Run as background service
asyncio.run(run_enrichment_service())
```

---

### Execution Modes

```python
# Dry run - no database writes
runner = EnrichmentRunner(db, run_mode="dry_run")
await runner.enrich_batch()
# → Logs what would be written, but doesn't write

# Safe run - writes enrichment observations (DEFAULT)
runner = EnrichmentRunner(db, run_mode="safe_run")
await runner.enrich_batch()
# → Writes enrichment observations to database

# Full run - same as safe_run (all enrichment is append-only)
runner = EnrichmentRunner(db, run_mode="full_run")
await runner.enrich_batch()
# → Writes all observations
```

---

### Data Structures

#### Enrichment Observation (stored in phone_identities)
```python
{
    "field_name": "office_address",
    "value": "123 Main St, Istanbul",
    "source": "google_places",
    "timestamp": datetime.utcnow(),
    "evidence_id": "5f9c4ab0-..."
}
```

#### Source Evidence (SourceEvidence collection)
```python
{
    "id": "5f9c4ab0-...",
    "phone_e164": "+905551234567",
    "source": "google_places",
    "url": "enrichment://google_places/+905551234567",
    "fields_detected": ["office_address"],
    "raw_html_hash": None,
    "timestamp": datetime.utcnow(),
    "confidence": "high"
}
```

---

### Candidate Selection

Phones are selected for enrichment if:

1. **Status** = 'active'
2. **Confidence** < 0.85 OR not enriched in last 24 hours
3. **Office coverage** < 80% of profiles have office names

**Example Query**:
```javascript
db.phone_identities.find({
    status: "active",
    confidence_score: {$lt: 0.85}
})
// Returns phones with low confidence needing enrichment
```

---

### Critical Invariants

✅ **No new phones created**
- `EnrichmentRunner.enrich()` only writes to existing phones

✅ **No overwrites**
- `add_enrichment_observation()` appends, never replaces

✅ **Evidence tracking**
- Every observation has corresponding SourceEvidence record

✅ **Graph enforcement**
- All writes through IdentityGraphResolver

✅ **Respects execution modes**
- dry_run: logs only
- safe_run: writes append-only observations
- full_run: writes all observations

---

### Error Handling

```python
# Individual errors don't block other phones
try:
    observations = await enricher.enrich(phone, fields)
    for obs in observations:
        graph.add_enrichment_observation(...)
except Exception as e:
    logger.error(f"Enrichment failed for {phone}: {e}")
    # Continue with next phone
```

---

### Monitoring

```python
# Check enrichment queue
queue = EnrichmentQueue(db)
candidates = queue.get_candidates(limit=100)
print(f"Phones needing enrichment: {len(candidates)}")

# Check enrichment observations added
enrichment_count = db.source_evidence.count_documents({
    "source": {"$in": ["google_places", "hepsiemlak"]}
})
print(f"Enrichment observations: {enrichment_count}")

# Check average observations per phone
result = db.phone_identities.aggregate([
    {"$group": {
        "_id": None,
        "avg_enrichment": {"$avg": {
            "$size": {"$ifNull": ["$enrichment_observations", []]}
        }}
    }}
])
print(f"Avg enrichment obs/phone: {list(result)[0]['avg_enrichment']:.2f}")
```

---

### Enricher Implementation (Template)

To implement a new enricher:

```python
class CustomEnricher:
    def __init__(self, db):
        self.db = db
    
    async def enrich(
        self,
        phone_e164: str,
        missing_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Return list of observations."""
        observations = []
        
        # Fetch data from external source
        if "office_name" in missing_fields:
            office_name = await self._fetch_office_name(phone_e164)
            if office_name:
                observations.append({
                    "field_name": "office_name",
                    "value": office_name,
                    "timestamp": datetime.utcnow()
                })
        
        return observations
    
    async def _fetch_office_name(self, phone: str) -> Optional[str]:
        # Implementation here
        pass
```

Then use:
```python
runner.google = CustomEnricher(db)  # Replace enricher
```

---

### Gotchas

❌ **Don't create new phones**
```python
# WRONG: Would try to create if phone_e164 not found
resolver.add_enrichment_observation(
    phone_e164="+905559999999",  # Doesn't exist!
    field_name="office_name",
    value="Test Office"
)
# → InvalidPhoneError
```

❌ **Don't overwrite existing fields**
```python
# WRONG: Enrichment only appends
# Existing agent_name won't be replaced by enrichment
# Both observations coexist in enrichment_observations array
```

❌ **Don't write without evidence**
```python
# WRONG: Missing SourceEvidence
db.phone_identities.update_one(
    {"phone_e164": phone},
    {"$push": {"enrichment_observations": {...}}}
)
# → Orphaned observation without evidence

# RIGHT: Always through add_enrichment_observation()
resolver.add_enrichment_observation(...)
# → Creates SourceEvidence + enrichment_observations
```

---

### Testing

```bash
python validate_step19_enrichment.py
```

Expected output:
```
✓ Phone Identities: 2 → 2 (no increase)
✓ Evidence Records: 7 → 8 (enrichment added)
✓ Enrichment Observations: 1
✓ Enrichment Sources: 1
✅ ALL VALIDATIONS PASSED
```

---

### Performance

- **Per phone**: ~5-50ms enrichment (depends on source)
- **Batch of 10**: ~100-500ms with timeout
- **Throughput**: 20-100 phones/second
- **Rate limiting**: Use batch_interval_seconds to avoid overwhelming sources

---

### Next Steps

1. **Implement Real Enrichers**
   - Hepsiemlak: Read public search results
   - Google Places: Query Places API

2. **STEP 20: Saturation Dashboard**
   - Track NEW_PHONE_RATE
   - Auto-stop when saturation reached

3. **STEP 21: Multi-City**
   - Extend enrichment to Ankara, İzmir
   - Per-city candidate selection
