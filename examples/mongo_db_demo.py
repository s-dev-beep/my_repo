"""MongoDB Demo - Example usage of database persistence layer.

This script demonstrates how to use the MongoDBConnection to persist
normalized listing data and related entities (offices, agents) with
proper upsert semantics.

The MongoDB layer:
1. Accepts normalized data from STEP 5
2. Upserts offices and agents based on deduplication keys
3. Upserts listings with references to their offices/agents
4. Returns operation indicators (inserted/updated)
5. Never performs blind inserts - always idempotent

Usage:
    # Set MongoDB URI
    export MONGO_URI="mongodb://localhost:27017"
    
    # Run the demo
    python examples/mongo_db_demo.py
"""

from src.db.mongo import MongoDBConnection


# ============================================================================
# NORMALIZED DATA EXAMPLES (FROM STEP 5)
# ============================================================================

# Example 1: Complete office listing with all contact info (high confidence)
OFFICE_LISTING_NORMALIZED = {
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456',
    'office_name': 'EV GAYRIMENKUL',
    'agent_name': 'AHMET YILMAZ',
    'phone_number': '+905321234567',
    'city': 'İstanbul',
    'district': 'Kadıköy',
    'source': 'sahibinden',
    'confidence': 'high'
}

# Example 2: Same office and agent from different district (different listing)
OFFICE_LISTING_DIFFERENT_LOCATION = {
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-besiktas-999999',
    'office_name': 'EV GAYRIMENKUL',
    'agent_name': 'AHMET YILMAZ',
    'phone_number': '+905321234567',
    'city': 'İstanbul',
    'district': 'Beşiktaş',  # Different location, same office/agent
    'source': 'sahibinden',
    'confidence': 'high'
}

# Example 3: Duplicate listing (same URL - should update)
OFFICE_LISTING_DUPLICATE = {
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456',
    'office_name': 'EV GAYRIMENKUL',
    'agent_name': 'AHMET YILMAZ',
    'phone_number': '+905321234567',
    'city': 'İstanbul',
    'district': 'Kadıköy',
    'source': 'sahibinden',
    'confidence': 'high'
}

# Example 4: Private seller with minimal contact info
PRIVATE_SELLER = {
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-ankara-12345',
    'office_name': None,
    'agent_name': 'MEHMET DEMIR',
    'phone_number': '+905558889900',
    'city': 'Ankara',
    'district': 'Çankaya',
    'source': 'sahibinden',
    'confidence': 'medium'
}

# Example 5: Same private seller (duplicate agent, different listing)
PRIVATE_SELLER_ANOTHER_LISTING = {
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-ankara-67890',
    'office_name': None,
    'agent_name': 'MEHMET DEMIR',
    'phone_number': '+905558889900',  # Same phone as Example 4
    'city': 'Ankara',
    'district': 'Kızılcaahamam',
    'source': 'sahibinden',
    'confidence': 'medium'
}

# Example 6: Very incomplete listing (missing office and agent)
INCOMPLETE_LISTING = {
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-izmir-77777',
    'office_name': None,
    'agent_name': None,
    'phone_number': None,
    'city': 'İzmir',
    'district': 'Alsancak',
    'source': 'sahibinden',
    'confidence': 'low'
}

# Example 7: Agent with only name (missing phone - cannot deduplicate)
AGENT_ONLY_NAME = {
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-bursa-456',
    'office_name': None,
    'agent_name': 'FATMA KAPLAN',
    'phone_number': None,  # Missing phone - cannot deduplicate agent
    'city': 'Bursa',
    'district': 'Nilüfer',
    'source': 'sahibinden',
    'confidence': 'low'
}


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def demo_basic_upsert():
    """Demo 1: Basic upsert operations."""
    print_section("Demo 1: Basic Upsert Operations")
    
    try:
        with MongoDBConnection() as db:
            # Upsert a complete listing
            print("1️⃣  Upserting complete office listing...")
            listing_id, op = db.upsert_listing(OFFICE_LISTING_NORMALIZED)
            print(f"   ✓ {op.title()}: {listing_id}")
            
            # Retrieve the listing
            print("\n2️⃣  Retrieving the listing...")
            listing = db.get_listing(OFFICE_LISTING_NORMALIZED['listing_url'])
            if listing:
                print(f"   ✓ Found listing:")
                print(f"     - URL: {listing['listing_url']}")
                print(f"     - Office: {listing['office_name']}")
                print(f"     - Agent: {listing['agent_name']}")
                print(f"     - Office ID: {listing.get('office_id')}")
                print(f"     - Agent ID: {listing.get('agent_id')}")
            
            # Upsert the same listing again (should update, not insert)
            print("\n3️⃣  Upserting the SAME listing again...")
            listing_id2, op2 = db.upsert_listing(OFFICE_LISTING_NORMALIZED)
            print(f"   ✓ {op2.title()}: {listing_id2}")
            assert listing_id == listing_id2, "Should be same ID!"
            assert op2 == 'updated', "Should be updated!"
            
            # Different listing, same office/agent
            print("\n4️⃣  Upserting different listing with SAME office/agent...")
            listing_id3, op3 = db.upsert_listing(OFFICE_LISTING_DIFFERENT_LOCATION)
            print(f"   ✓ {op3.title()}: {listing_id3}")
            
            # Check office was reused
            office = db.get_office('EV GAYRIMENKUL', '+905321234567')
            if office:
                print(f"   ✓ Office exists with ID: {office['_id']}")
                print(f"     (both listings should reference this office)")
            
            print("\n✅ Demo 1 completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_agent_deduplication():
    """Demo 2: Agent deduplication (phone-based)."""
    print_section("Demo 2: Agent Deduplication")
    
    try:
        with MongoDBConnection() as db:
            # Upsert private seller listing
            print("1️⃣  Upserting private seller listing...")
            listing_id1, op1 = db.upsert_listing(PRIVATE_SELLER)
            print(f"   ✓ {op1.title()}: {listing_id1}")
            
            # Upsert another listing from same agent
            print("\n2️⃣  Upserting another listing from SAME agent...")
            listing_id2, op2 = db.upsert_listing(PRIVATE_SELLER_ANOTHER_LISTING)
            print(f"   ✓ {op2.title()}: {listing_id2}")
            
            # Check agent was reused
            agent = db.get_agent('MEHMET DEMIR', '+905558889900')
            if agent:
                print(f"\n3️⃣  Checking agent deduplication...")
                print(f"   ✓ Agent exists with ID: {agent['_id']}")
                print(f"     (both listings should reference this agent)")
                print(f"     Created: {agent.get('created_at')}")
                print(f"     Updated: {agent.get('updated_at')}")
            
            print("\n✅ Demo 2 completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_incomplete_data():
    """Demo 3: Handling incomplete data (missing dedup keys)."""
    print_section("Demo 3: Handling Incomplete Data")
    
    try:
        with MongoDBConnection() as db:
            # Upsert incomplete listing
            print("1️⃣  Upserting very incomplete listing...")
            print("    (no office, agent, or phone)")
            listing_id1, op1 = db.upsert_listing(INCOMPLETE_LISTING)
            print(f"   ✓ {op1.title()}: {listing_id1}")
            print("    (listing still stored, but no office/agent references)")
            
            # Upsert agent with only name (no phone)
            print("\n2️⃣  Upserting listing with agent name but no phone...")
            listing_id2, op2 = db.upsert_listing(AGENT_ONLY_NAME)
            print(f"   ✓ {op2.title()}: {listing_id2}")
            print("    (agent deduplication skipped - no phone available)")
            
            listing = db.get_listing(AGENT_ONLY_NAME['listing_url'])
            if listing:
                print(f"    Agent ID: {listing.get('agent_id')}")
                print(f"    (None - because agent has no phone for dedup)")
            
            print("\n✅ Demo 3 completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_statistics():
    """Demo 4: Database statistics."""
    print_section("Demo 4: Database Statistics")
    
    try:
        with MongoDBConnection() as db:
            stats = db.get_stats()
            
            print("📊 Current database state:")
            print(f"   Listings: {stats['listings']}")
            print(f"   Offices:  {stats['offices']}")
            print(f"   Agents:   {stats['agents']}")
            
            print("\n✅ Demo 4 completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_idempotency():
    """Demo 5: Idempotency - running same insert twice."""
    print_section("Demo 5: Idempotency Testing")
    
    try:
        with MongoDBConnection() as db:
            url = 'https://www.sahibinden.com/ilan/idempotency-test-xyz'
            
            data = {
                'listing_url': url,
                'office_name': 'TEST OFFICE',
                'agent_name': 'TEST AGENT',
                'phone_number': '+905555555555',
                'city': 'İstanbul',
                'district': 'Test',
                'source': 'test',
                'confidence': 'high'
            }
            
            # First insert
            print("1️⃣  First insert...")
            id1, op1 = db.upsert_listing(data)
            print(f"   ✓ Operation: {op1}")
            print(f"   ✓ ID: {id1}")
            
            # Second insert (same data)
            print("\n2️⃣  Second insert (identical data)...")
            id2, op2 = db.upsert_listing(data)
            print(f"   ✓ Operation: {op2}")
            print(f"   ✓ ID: {id2}")
            
            # Verify
            if id1 == id2 and op2 == 'updated':
                print("\n✅ Idempotency verified!")
                print("   Same input → same ID, updated operation")
            else:
                print("\n⚠️  Idempotency issue detected!")
            
            # Update the data slightly
            print("\n3️⃣  Partial update (new district)...")
            data['district'] = 'Updated District'
            id3, op3 = db.upsert_listing(data)
            print(f"   ✓ Operation: {op3}")
            print(f"   ✓ ID: {id3}")
            
            if id1 == id3 and op3 == 'updated':
                print("\n✅ Update verified!")
                print("   Same URL → same ID, updated with new data")
            
            print("\n✅ Demo 5 completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  MongoDB Persistence Layer - Example Usage")
    print("  STEP 7: Database Persistence")
    print("=" * 80)
    
    print("\n⚠️  Note: This demo requires MongoDB to be running.")
    print("   Set MONGO_URI environment variable to connect:")
    print("   export MONGO_URI='mongodb://localhost:27017'")
    
    try:
        # Try to run demos
        demo_basic_upsert()
        demo_agent_deduplication()
        demo_incomplete_data()
        demo_statistics()
        demo_idempotency()
        
        print("\n" + "=" * 80)
        print("  ✅ All demos completed!")
        print("=" * 80 + "\n")
    
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure MongoDB is running")
        print("2. Set MONGO_URI environment variable")
        print("3. Check connection string format")


if __name__ == "__main__":
    main()
