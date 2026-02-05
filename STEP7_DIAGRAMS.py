"""STEP 7: SCHEMA DESIGN & DATA FLOW DIAGRAMS

Visual representations of the MongoDB collections and data flow.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# COLLECTION SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

OFFICE_SCHEMA = """
┌─────────────────────────────────────────────────────────────┐
│                    OFFICES COLLECTION                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  _id: ObjectId                                             │
│  office_name: String | null        ← Dedup key (part 1)   │
│  phone_number: String | null       ← Dedup key (part 2)   │
│  created_at: DateTime                                      │
│  updated_at: DateTime                                      │
│                                                             │
│  Index: (office_name, phone_number) SPARSE                │
│  → Enables efficient dedup lookups                         │
│  → Handles null values properly                            │
│  → Not strictly unique (allow both null)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Example documents:

  // Real estate company with contact
  {
    _id: ObjectId("507f1f77bcf86cd799439011"),
    office_name: "EV GAYRIMENKUL",
    phone_number: "+905321234567",
    created_at: 2024-02-01T10:30:00Z,
    updated_at: 2024-02-01T14:45:00Z
  }

  // Office with only phone (no name)
  {
    _id: ObjectId("507f1f77bcf86cd799439012"),
    office_name: null,
    phone_number: "+905558889900",
    created_at: 2024-02-01T11:00:00Z,
    updated_at: 2024-02-01T15:00:00Z
  }

  // Office with only name (no phone - rare)
  {
    _id: ObjectId("507f1f77bcf86cd799439013"),
    office_name: "PREMIUM EMLAK",
    phone_number: null,
    created_at: 2024-02-01T12:00:00Z,
    updated_at: 2024-02-01T16:00:00Z
  }
"""

AGENT_SCHEMA = """
┌─────────────────────────────────────────────────────────────┐
│                    AGENTS COLLECTION                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  _id: ObjectId                                             │
│  agent_name: String | null        ← Dedup key (part 1)    │
│  phone_number: String | null      ← Dedup key (part 2)    │
│  created_at: DateTime                                      │
│  updated_at: DateTime                                      │
│                                                             │
│  Index: (agent_name, phone_number) SPARSE                 │
│  → Enables efficient dedup lookups                         │
│  → Handles null values properly                            │
│  → Not strictly unique (allow both null)                   │
│                                                             │
│  Note: Identical structure to OFFICES, different meaning   │
│        (can be independent agents, company employees, etc) │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Example documents:

  // Named agent with phone
  {
    _id: ObjectId("507f1f77bcf86cd799439020"),
    agent_name: "AHMET YILMAZ",
    phone_number: "+905321234567",
    created_at: 2024-02-01T10:35:00Z,
    updated_at: 2024-02-01T14:50:00Z
  }

  // Private seller (no name, just phone)
  {
    _id: ObjectId("507f1f77bcf86cd799439021"),
    agent_name: null,
    phone_number: "+905558889900",
    created_at: 2024-02-01T11:05:00Z,
    updated_at: 2024-02-01T15:05:00Z
  }
"""

LISTING_SCHEMA = """
┌──────────────────────────────────────────────────────────────────────┐
│                    LISTINGS COLLECTION                              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  _id: ObjectId                                                      │
│                                                                      │
│  ┌─ UNIQUE IDENTIFIER ─────────────────────────────────────────┐   │
│  │ listing_url: String (REQUIRED, UNIQUE)                      │   │
│  │             ← Primary dedup key                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─ CONTACT INFORMATION ───────────────────────────────────────┐   │
│  │ office_name: String | null    (from normalized data)       │   │
│  │ agent_name: String | null     (from normalized data)       │   │
│  │ phone_number: String | null   (E.164 format)               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─ LOCATION INFORMATION ──────────────────────────────────────┐   │
│  │ city: String | null           (title case)                 │   │
│  │ district: String | null       (title case)                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─ SOURCE & QUALITY ──────────────────────────────────────────┐   │
│  │ source: String | null         (sahibinden, hepsiemlak)     │   │
│  │ confidence: String | null     (high, medium, low)          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─ RELATIONSHIPS ─────────────────────────────────────────────┐   │
│  │ office_id: ObjectId | null   → reference to OFFICES        │   │
│  │ agent_id: ObjectId | null    → reference to AGENTS         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─ METADATA ──────────────────────────────────────────────────┐   │
│  │ created_at: DateTime          (when first persisted)       │   │
│  │ updated_at: DateTime          (last update time)           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Index: UNIQUE on listing_url                                      │
│  → Ensures one listing per URL                                     │
│  → Enables fast lookups                                            │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

Example document (complete):

  {
    _id: ObjectId("507f1f77bcf86cd799439030"),
    listing_url: "https://www.sahibinden.com/ilan/123456",
    office_name: "EV GAYRIMENKUL",
    agent_name: "AHMET YILMAZ",
    phone_number: "+905321234567",
    city: "İstanbul",
    district: "Kadıköy",
    source: "sahibinden",
    confidence: "high",
    office_id: ObjectId("507f1f77bcf86cd799439011"),
    agent_id: ObjectId("507f1f77bcf86cd799439020"),
    created_at: 2024-02-01T10:30:00Z,
    updated_at: 2024-02-01T10:30:00Z
  }

Example document (incomplete):

  {
    _id: ObjectId("507f1f77bcf86cd799439031"),
    listing_url: "https://www.sahibinden.com/ilan/999999",
    office_name: null,
    agent_name: null,
    phone_number: null,
    city: "İzmir",
    district: null,
    source: "sahibinden",
    confidence: "low",
    office_id: null,
    agent_id: null,
    created_at: 2024-02-01T11:00:00Z,
    updated_at: 2024-02-01T11:00:00Z
  }
"""

# ═══════════════════════════════════════════════════════════════════════════════
# RELATIONSHIP DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════════

RELATIONSHIP_DIAGRAM = """
┌──────────────┐        ┌──────────────┐
│   OFFICES    │        │    AGENTS    │
├──────────────┤        ├──────────────┤
│ _id          │        │ _id          │
│ name+phone   │        │ name+phone   │
│ (dedup key)  │        │ (dedup key)  │
└──────────────┘        └──────────────┘
       ▲                       ▲
       │                       │
       │ office_id             │ agent_id
       │ (optional ref)        │ (optional ref)
       │                       │
       └───────────┬───────────┘
                   │
            ┌──────▼───────┐
            │   LISTINGS   │
            ├──────────────┤
            │ _id          │
            │ listing_url  │
            │ (unique key) │
            │              │
            │ Contains:    │
            │ - contact    │
            │ - location   │
            │ - refs to    │
            │   office     │
            │   agent      │
            └──────────────┘

Relationship semantics:
- A Listing may reference an Office (office_id)
  → Office is optional (private sellers have no office)
  → Multiple listings can reference same office

- A Listing may reference an Agent (agent_id)
  → Agent is optional (incomplete contact info)
  → Multiple listings can reference same agent

- An Office is referenced by zero or more Listings
  → Enables queries like "all listings from this office"

- An Agent is referenced by zero or more Listings
  → Enables queries like "all listings from this agent"
"""

# ═══════════════════════════════════════════════════════════════════════════════
# DATA FLOW DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════════

DATA_FLOW_DIAGRAM = """
STEP 7: DATABASE PERSISTENCE FLOW

Raw Data (from parser)
      │
      ▼
┌─────────────────────┐
│  STEP 5: NORMALIZE  │
│  - Clean names      │
│  - Normalize phones │
│  - Trim/case cities │
└─────────────────────┘
      │
      ▼
Normalized Data: {
  listing_url: "https://...",
  office_name: "EV GAYRIMENKUL",
  agent_name: "AHMET YILMAZ",
  phone_number: "+905321234567",
  city: "İstanbul",
  district: "Kadıköy",
  source: "sahibinden",
  confidence: "high"
}
      │
      ▼
┌─────────────────────────────┐
│  STEP 6: DEDUPLICATE        │
│  (in-memory check)          │
│  - Check if listing is new  │
│  - Check if office is new   │
│  - Check if agent is new    │
└─────────────────────────────┘
      │
      ▼
DeduplicationResult: {
  is_new: True,
  dedupe_key: "https://...",
  reason: "New listing URL"
}
      │
      ▼
┌──────────────────────────────────────┐
│  STEP 7: PERSIST (THIS LAYER)        │
│                                      │
│  1. Extract normalized data          │
│  2. Upsert Office (if possible)      │
│  3. Upsert Agent (if possible)       │
│  4. Upsert Listing                   │
│  5. Return (listing_id, operation)   │
└──────────────────────────────────────┘
      │
      ├─→ Check Office filter: (office_name, phone_number)
      │   • If exists: update + return 'updated'
      │   • If not: insert + return 'inserted'
      │
      ├─→ Check Agent filter: (agent_name, phone_number)
      │   • If exists: update + return 'updated'
      │   • If not: insert + return 'inserted'
      │
      └─→ Check Listing filter: listing_url
          • If exists: update + return 'updated'
          • If not: insert + return 'inserted'
      │
      ▼
MongoDB Collections:
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   OFFICES    │ │    AGENTS    │ │  LISTINGS    │
├──────────────┤ ├──────────────┤ ├──────────────┤
│ _id: ...     │ │ _id: ...     │ │ _id: ...     │
│ name: ...    │ │ name: ...    │ │ url: ...     │
│ phone: ...   │ │ phone: ...   │ │ office_id: →─┼─→ (ref)
│              │ │              │ │ agent_id:  →─┼─→ (ref)
└──────────────┘ └──────────────┘ │ contact: ... │
                                 │ location:... │
                                 └──────────────┘
      │
      ▼
Result: (listing_id: str, operation: 'inserted'|'updated')

Example result for new listing:
  ('507f1f77bcf86cd799439030', 'inserted')

Example result for duplicate listing:
  ('507f1f77bcf86cd799439030', 'updated')
"""

# ═══════════════════════════════════════════════════════════════════════════════
# UPSERT DECISION TREES
# ═══════════════════════════════════════════════════════════════════════════════

UPSERT_OFFICE_DECISION = """
OFFICE UPSERT LOGIC

Input: (office_name, phone_number)
       │
       ├─ Both null?
       │  YES → Log warning, still proceed
       │        (unlikely in practice)
       │
       └─ Build filter query
          ├─ If office_name exists: add to filter
          └─ If phone_number exists: add to filter
          │
          ▼
       Query: db.offices.update_one(filter, update, upsert=True)
       
       Case 1: Document exists matching filter
       ├─ Update office_name, phone_number
       ├─ Set updated_at = now
       ├─ Keep created_at unchanged
       └─ Return (id, 'updated')
       
       Case 2: No document matches filter
       ├─ Insert new document
       ├─ Set created_at = now
       ├─ Set updated_at = now
       └─ Return (id, 'inserted')
"""

UPSERT_LISTING_DECISION = """
LISTING UPSERT LOGIC

Input: normalized_data dict with listing_url (REQUIRED)
       │
       ├─ listing_url missing?
       │  YES → Raise ValueError
       │  NO  → Continue
       │
       ▼
    Extract fields:
    ├─ office_name, phone_number
    ├─ agent_name, phone_number (may be same or different)
    ├─ city, district, source, confidence
    │
    ▼
    Upsert Office (if office_name AND phone_number exist)
    │
    ├─ Call upsert_office(office_name, phone_number)
    ├─ Store returned office_id
    │
    ▼
    Upsert Agent (if agent_name AND phone_number exist)
    │
    ├─ Call upsert_agent(agent_name, phone_number)
    ├─ Store returned agent_id
    │
    ▼
    Query: db.listings.update_one({listing_url: url}, update, upsert=True)
    
    Case 1: Document exists with same URL
    ├─ Update all fields (office_name, agent_name, city, etc)
    ├─ Update references (office_id, agent_id)
    ├─ Set updated_at = now
    ├─ Keep created_at unchanged
    └─ Return (id, 'updated')
    
    Case 2: No document with this URL
    ├─ Insert new document
    ├─ Set all fields from normalized_data
    ├─ Set office_id and agent_id from upserts
    ├─ Set created_at = now
    ├─ Set updated_at = now
    └─ Return (id, 'inserted')
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PRINT DIAGRAMS
# ═══════════════════════════════════════════════════════════════════════════════

def print_all_diagrams():
    """Print all schema diagrams."""
    print("\n" + "=" * 80)
    print("STEP 7: SCHEMA DESIGN & DATA FLOW")
    print("=" * 80)
    
    print("\n1. OFFICE COLLECTION SCHEMA")
    print("-" * 80)
    print(OFFICE_SCHEMA)
    
    print("\n2. AGENT COLLECTION SCHEMA")
    print("-" * 80)
    print(AGENT_SCHEMA)
    
    print("\n3. LISTING COLLECTION SCHEMA")
    print("-" * 80)
    print(LISTING_SCHEMA)
    
    print("\n4. RELATIONSHIP DIAGRAM")
    print("-" * 80)
    print(RELATIONSHIP_DIAGRAM)
    
    print("\n5. DATA FLOW DIAGRAM")
    print("-" * 80)
    print(DATA_FLOW_DIAGRAM)
    
    print("\n6. OFFICE UPSERT DECISION TREE")
    print("-" * 80)
    print(UPSERT_OFFICE_DECISION)
    
    print("\n7. LISTING UPSERT DECISION TREE")
    print("-" * 80)
    print(UPSERT_LISTING_DECISION)
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_all_diagrams()
