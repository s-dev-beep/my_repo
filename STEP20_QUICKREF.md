# STEP 20: Saturation Measurement - Quick Reference

## Module Overview

| Module | Purpose | Key Classes |
|--------|---------|------------|
| `saturation_metrics.py` | Compute core saturation metrics | `SaturationMetricsComputer` |
| `district_tracker.py` | Track per-district saturation | `DistrictTracker` |
| `city_completion.py` | Assess city-level completion | `CityCompletion` |
| `stopping_rules.py` | Implement stopping decision logic | `StoppingRuleSet` |
| `saturation_snapshot.py` | Generate JSON snapshots | `SaturationSnapshot` |

---

## Metrics at a Glance

### NEW_PHONE_RATE (0.0-1.0)
**What**: % of new phones in time window  
**Formula**: `new_phones_in_window / total_active_in_window`  
**Interpretation**: 1.0 = discovering, 0.0 = saturated  
**Thresholds**:
- ✓ >= 0.05 (>= 5%) = HEALTHY
- ⚠️  < 0.05 (< 5%) = CONCERNING
- ❌ < 0.02 (< 2%) = CRITICAL

### PHONE_REVISIT_RATE (0.0-1.0)
**What**: % of phones with multiple observations  
**Formula**: `revisited_phones / total_active_in_window`  
**Interpretation**: 0.2 = mostly new, 0.9 = mostly revisits  
**Thresholds**:
- ✓ <= 0.80 (<= 80%) = HEALTHY
- ⚠️  > 0.80 (> 80%) = CONCERNING
- ❌ > 0.90 (> 90%) = CRITICAL

### ENRICHMENT_YIELD (0.0-1.0+)
**What**: Effectiveness of enrichment process  
**Formula**: `(enriched_phones / active_phones) * (1 + quality_improvement)`  
**Interpretation**: 0.0 = no enrichment, 1.0+ = high improvement  
**Thresholds**:
- ✓ >= 0.10 (>= 10%) = ACTIVE
- ⚠️  < 0.10 (< 10%) = CONCERNING
- ❌ < 0.05 (< 5%) = CRITICAL

### PER_DISTRICT_COVERAGE
**What**: Coverage and saturation by district  
**Returns**: For each district:
- `phone_count`: unique phones
- `growth_rate`: new phones / total in 24h
- `confidence_avg`: average confidence score

---

## Status Values

### District Status
- **ACTIVE**: growth_rate >= 5%, discovery happening
- **SLOWING**: growth_rate < 5% OR confidence > 0.90
- **SATURATED**: growth_rate < 2% AND total_phones >= 50

### City Status
- **ACTIVE**: saturation_score < 0.50, active discovery
- **MATURING**: 0.50 <= saturation_score < 0.80, slowing discovery
- **READY_TO_STOP**: saturation_score >= 0.80 AND confidence >= 0.85 AND phones >= 500

---

## Stopping Decision

**Should STOP if and only if ALL are true:**
1. city_status == READY_TO_STOP
2. No CRITICAL rule violations
3. confidence_avg >= 0.85
4. total_phones >= 500

**CONSERVATIVE**: Requires multiple signals, not single metric spike.

---

## Code Examples

### 1. Quick Stopping Check
```python
from pymongo import MongoClient
from src.analytics import StoppingRuleSet

client = MongoClient()
db = client.real_estate
rules = StoppingRuleSet(db, city="Istanbul")

should_stop, evidence = rules.should_stop_crawling()
print(f"Ready to stop: {should_stop}")
```

### 2. Get All Metrics
```python
from src.analytics import SaturationMetricsComputer

metrics = SaturationMetricsComputer(db)
all_metrics = metrics.compute_all_metrics(window_hours=24)

print(f"NEW_PHONE_RATE: {all_metrics['new_phone_rate']['rate']:.1%}")
print(f"REVISIT_RATE: {all_metrics['phone_revisit_rate']['rate']:.1%}")
```

### 3. Check District Status
```python
from src.analytics import DistrictTracker

tracker = DistrictTracker(db, city="Istanbul")
status = tracker.get_district_status("Kadıköy")

print(f"Status: {status['status']}")
print(f"Growth: {status['growth_rate']:.1%}")
```

### 4. Generate Report
```python
from src.analytics import SaturationSnapshot

snapshot_gen = SaturationSnapshot(db)
snapshot = snapshot_gen.create_and_save_snapshot(run_id="crawl_20260202")

print(snapshot_gen.generate_summary_report(snapshot))
```

### 5. Track Trends
```python
snap1 = snapshot_gen.load_snapshot("reports/saturation_snapshot_20260201.json")
snap2 = snapshot_gen.load_snapshot("reports/saturation_snapshot_20260202.json")

comparison = snapshot_gen.compare_snapshots(snap1, snap2)
print(comparison['analysis'])
```

---

## Key Thresholds

```
# Saturation Detection (Individual Metrics)
NEW_PHONE_RATE          < 5%      → Slowing
NEW_PHONE_RATE          < 2%      → Critical
PHONE_REVISIT_RATE      > 80%     → High revisits
PHONE_REVISIT_RATE      > 90%     → Critical revisits
ENRICHMENT_YIELD        < 10%     → Diminishing
ENRICHMENT_YIELD        < 5%      → Exhausted

# District-Level
DISTRICT_GROWTH         < 5%      → Slowing
DISTRICT_GROWTH         < 2%      → Saturated (if >= 50 phones)
DISTRICT_CONFIDENCE     > 0.90    → Complete

# City-Level
CITY_SATURATION         >= 0.80   → Ready
CITY_CONFIDENCE         >= 0.85   → High quality
CITY_PHONES             >= 500    → Meaningful sample
SATURATED_DISTRICTS     >= 50%    → Concerning
```

---

## Workflow

```
1. Compute Metrics
   └─ NEW_PHONE_RATE, REVISIT_RATE, ENRICHMENT_YIELD, COVERAGE

2. Track Districts
   └─ Status (ACTIVE/SLOWING/SATURATED), Saturation Score

3. Assess City
   └─ Status (ACTIVE/MATURING/READY_TO_STOP), Projection

4. Evaluate Rules
   └─ Check all thresholds against metrics

5. Make Decision
   └─ Should_stop = ALL criteria met (conservative)

6. Generate Report
   └─ JSON snapshot, trends, recommendations

7. Take Action
   └─ CONTINUE or PREPARE TO STOP based on decision
```

---

## Files

### Source Code
```
src/analytics/
  ├── __init__.py
  ├── saturation_metrics.py
  ├── district_tracker.py
  ├── city_completion.py
  ├── stopping_rules.py
  └── saturation_snapshot.py
```

### Tests & Examples
```
validate_step20_saturation.py    # Comprehensive validation
examples/saturation_demo.py       # Live MongoDB integration
```

### Documentation
```
STEP20_COMPLETE.md               # Full specification
STEP20_QUICKREF.md               # This file
```

---

## Validation Status

✅ All tests passed:
- Synthetic data validation
- Metric calculations
- District saturation logic
- City completion assessment
- Stopping decision thresholds

---

## Integration Points

Works with:
- ✓ STEP 17: Identity Graph (immutable)
- ✓ STEP 18: Crawler Integration (identity writes)
- ✓ STEP 19: Enrichment (read-only observations)

No interaction with:
- ✗ Live crawling
- ✗ Enrichment processes
- ✗ Database writes
- ✗ Schema changes

---

## Key Properties

| Property | Value |
|----------|-------|
| READ_ONLY | Yes - No DB writes |
| Deterministic | Yes - Same input = Same output |
| Scalable | Yes - Works for any city |
| Conservative | Yes - Multiple signals required |
| Documented | Yes - Thresholds explicit |
| Validated | Yes - All tests pass |

---

**For full details, see STEP20_COMPLETE.md**
