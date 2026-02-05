"""Test suite for the Deduplicator module (STEP 6).

Tests cover:
- Listing deduplication (by URL)
- Office deduplication (by name + phone)
- Agent deduplication (by name + phone)
- Edge cases (missing fields, empty values, invalid input)
- Batch loading
- Statistics

Usage:
    python -m pytest test_deduplicator.py -v
    python test_deduplicator.py (run with unittest)
"""

import unittest
from src.core.deduplicator import Deduplicator, DeduplicationResult


class TestListingDeduplication(unittest.TestCase):
    """Test cases for listing deduplication by URL."""
    
    def setUp(self):
        """Initialize deduplicator before each test."""
        self.dedup = Deduplicator()
    
    def test_new_listing(self):
        """Test that new listing is detected correctly."""
        data = {'listing_url': 'https://www.sahibinden.com/ilan/123'}
        result = self.dedup.check_listing(data)
        
        self.assertTrue(result.is_new)
        self.assertEqual(result.dedupe_key, 'https://www.sahibinden.com/ilan/123')
        self.assertIn("New listing", result.reason)
    
    def test_duplicate_listing(self):
        """Test that duplicate listing is detected."""
        url = 'https://www.sahibinden.com/ilan/123'
        self.dedup.add_listing(url)
        
        data = {'listing_url': url}
        result = self.dedup.check_listing(data)
        
        self.assertFalse(result.is_new)
        self.assertEqual(result.dedupe_key, url)
        self.assertIn("already seen", result.reason)
    
    def test_missing_listing_url(self):
        """Test that missing URL cannot be deduplicated."""
        data = {'office_name': 'Test Office'}  # No listing_url
        result = self.dedup.check_listing(data)
        
        self.assertTrue(result.is_new)  # Treated as new
        self.assertIsNone(result.dedupe_key)
        self.assertIn("missing", result.reason.lower())
    
    def test_empty_listing_url(self):
        """Test that empty URL cannot be deduplicated."""
        data = {'listing_url': ''}
        result = self.dedup.check_listing(data)
        
        self.assertTrue(result.is_new)
        self.assertIsNone(result.dedupe_key)
    
    def test_add_listing_duplicate(self):
        """Test adding the same listing twice."""
        url = 'https://www.sahibinden.com/ilan/123'
        self.dedup.add_listing(url)
        self.dedup.add_listing(url)  # Add again
        
        # Should still be detected as duplicate once
        data = {'listing_url': url}
        result = self.dedup.check_listing(data)
        self.assertFalse(result.is_new)
    
    def test_invalid_input_type(self):
        """Test that non-dict input raises ValueError."""
        with self.assertRaises(ValueError):
            self.dedup.check_listing("not a dict")
        
        with self.assertRaises(ValueError):
            self.dedup.check_listing(123)
    
    def test_multiple_different_listings(self):
        """Test handling multiple different listings."""
        urls = [
            'https://www.sahibinden.com/ilan/1',
            'https://www.sahibinden.com/ilan/2',
            'https://www.hepsiemlak.com/ilan/1',
        ]
        
        for url in urls:
            self.dedup.add_listing(url)
        
        stats = self.dedup.stats()
        self.assertEqual(stats['listings'], 3)
        
        # All should be detected as duplicates
        for url in urls:
            result = self.dedup.check_listing({'listing_url': url})
            self.assertFalse(result.is_new)


class TestOfficeDeduplication(unittest.TestCase):
    """Test cases for office deduplication by name + phone."""
    
    def setUp(self):
        """Initialize deduplicator before each test."""
        self.dedup = Deduplicator()
    
    def test_new_office(self):
        """Test that new office is detected correctly."""
        data = {
            'office_name': 'EV GAYRIMENKUL',
            'phone_number': '+905321234567'
        }
        result = self.dedup.check_office(data)
        
        self.assertTrue(result.is_new)
        self.assertIsNotNone(result.dedupe_key)
        self.assertIn("EV GAYRIMENKUL", result.reason)
    
    def test_duplicate_office(self):
        """Test that duplicate office is detected."""
        name = 'EV GAYRIMENKUL'
        phone = '+905321234567'
        self.dedup.add_office(name, phone)
        
        data = {
            'office_name': name,
            'phone_number': phone
        }
        result = self.dedup.check_office(data)
        
        self.assertFalse(result.is_new)
        self.assertIn("already seen", result.reason)
    
    def test_missing_office_name(self):
        """Test that missing office name cannot be deduplicated."""
        data = {
            'office_name': None,
            'phone_number': '+905321234567'
        }
        result = self.dedup.check_office(data)
        
        self.assertTrue(result.is_new)  # Treated as new
        self.assertIsNone(result.dedupe_key)
        self.assertIn("office_name", result.reason)
    
    def test_missing_phone(self):
        """Test that missing phone cannot be deduplicated."""
        data = {
            'office_name': 'EV GAYRIMENKUL',
            'phone_number': None
        }
        result = self.dedup.check_office(data)
        
        self.assertTrue(result.is_new)
        self.assertIsNone(result.dedupe_key)
        self.assertIn("phone_number", result.reason)
    
    def test_empty_office_name(self):
        """Test that empty office name cannot be deduplicated."""
        data = {
            'office_name': '',
            'phone_number': '+905321234567'
        }
        result = self.dedup.check_office(data)
        
        self.assertTrue(result.is_new)
    
    def test_different_office_same_phone(self):
        """Test that different office with same phone is NEW."""
        office1 = ('EV GAYRIMENKUL', '+905321234567')
        office2 = ('PREMIUM EMLAK', '+905321234567')
        
        self.dedup.add_office(*office1)
        
        data = {
            'office_name': office2[0],
            'phone_number': office2[1]
        }
        result = self.dedup.check_office(data)
        
        # Should be NEW because name is different
        self.assertTrue(result.is_new)
    
    def test_same_office_different_phone(self):
        """Test that same office name with different phone is NEW."""
        name = 'EV GAYRIMENKUL'
        phone1 = '+905321234567'
        phone2 = '+905559999999'
        
        self.dedup.add_office(name, phone1)
        
        data = {
            'office_name': name,
            'phone_number': phone2
        }
        result = self.dedup.check_office(data)
        
        # Should be NEW because phone is different
        self.assertTrue(result.is_new)
    
    def test_invalid_input_type(self):
        """Test that non-dict input raises ValueError."""
        with self.assertRaises(ValueError):
            self.dedup.check_office("not a dict")
    
    def test_add_office_invalid_args(self):
        """Test that add_office validates arguments."""
        with self.assertRaises(ValueError):
            self.dedup.add_office('', '+905321234567')
        
        with self.assertRaises(ValueError):
            self.dedup.add_office('EV GAYRIMENKUL', '')


class TestAgentDeduplication(unittest.TestCase):
    """Test cases for agent deduplication by name + phone."""
    
    def setUp(self):
        """Initialize deduplicator before each test."""
        self.dedup = Deduplicator()
    
    def test_new_agent(self):
        """Test that new agent is detected correctly."""
        data = {
            'agent_name': 'AHMET YILMAZ',
            'phone_number': '+905321234567'
        }
        result = self.dedup.check_agent(data)
        
        self.assertTrue(result.is_new)
        self.assertIsNotNone(result.dedupe_key)
        self.assertIn("AHMET YILMAZ", result.reason)
    
    def test_duplicate_agent(self):
        """Test that duplicate agent is detected."""
        name = 'AHMET YILMAZ'
        phone = '+905321234567'
        self.dedup.add_agent(name, phone)
        
        data = {
            'agent_name': name,
            'phone_number': phone
        }
        result = self.dedup.check_agent(data)
        
        self.assertFalse(result.is_new)
        self.assertIn("already seen", result.reason)
    
    def test_missing_agent_name(self):
        """Test that missing agent name cannot be deduplicated."""
        data = {
            'agent_name': None,
            'phone_number': '+905321234567'
        }
        result = self.dedup.check_agent(data)
        
        self.assertTrue(result.is_new)
        self.assertIsNone(result.dedupe_key)
        self.assertIn("agent_name", result.reason)
    
    def test_missing_phone(self):
        """Test that missing phone cannot be deduplicated."""
        data = {
            'agent_name': 'AHMET YILMAZ',
            'phone_number': None
        }
        result = self.dedup.check_agent(data)
        
        self.assertTrue(result.is_new)
        self.assertIsNone(result.dedupe_key)
        self.assertIn("phone_number", result.reason)
    
    def test_different_agent_same_phone(self):
        """Test that different agent with same phone is NEW."""
        agent1 = ('AHMET YILMAZ', '+905321234567')
        agent2 = ('FATMA KAPLAN', '+905321234567')
        
        self.dedup.add_agent(*agent1)
        
        data = {
            'agent_name': agent2[0],
            'phone_number': agent2[1]
        }
        result = self.dedup.check_agent(data)
        
        # Should be NEW because name is different
        self.assertTrue(result.is_new)
    
    def test_same_agent_different_phone(self):
        """Test that same agent name with different phone is NEW."""
        name = 'AHMET YILMAZ'
        phone1 = '+905321234567'
        phone2 = '+905559999999'
        
        self.dedup.add_agent(name, phone1)
        
        data = {
            'agent_name': name,
            'phone_number': phone2
        }
        result = self.dedup.check_agent(data)
        
        # Should be NEW because phone is different
        self.assertTrue(result.is_new)


class TestBatchLoading(unittest.TestCase):
    """Test cases for batch loading entities."""
    
    def test_load_entities_empty_list(self):
        """Test loading empty list."""
        dedup = Deduplicator()
        dedup.load_entities([])
        
        stats = dedup.stats()
        self.assertEqual(stats['listings'], 0)
        self.assertEqual(stats['offices'], 0)
        self.assertEqual(stats['agents'], 0)
    
    def test_load_complete_entities(self):
        """Test loading entities with all fields."""
        dedup = Deduplicator()
        
        entities = [
            {
                'listing_url': 'https://www.sahibinden.com/ilan/1',
                'office_name': 'OFFICE1',
                'agent_name': 'AGENT1',
                'phone_number': '+905321111111',
            },
            {
                'listing_url': 'https://www.sahibinden.com/ilan/2',
                'office_name': 'OFFICE2',
                'agent_name': 'AGENT2',
                'phone_number': '+905322222222',
            },
        ]
        
        dedup.load_entities(entities)
        
        stats = dedup.stats()
        self.assertEqual(stats['listings'], 2)
        self.assertEqual(stats['offices'], 2)
        self.assertEqual(stats['agents'], 2)
    
    def test_load_partial_entities(self):
        """Test loading entities with missing fields."""
        dedup = Deduplicator()
        
        entities = [
            {
                'listing_url': 'https://www.sahibinden.com/ilan/1',
                'office_name': None,  # No office
                'agent_name': 'AGENT1',
                'phone_number': '+905321111111',
            },
            {
                'listing_url': 'https://www.sahibinden.com/ilan/2',
                # No agent_name
                'office_name': 'OFFICE2',
                'phone_number': '+905322222222',
            },
        ]
        
        dedup.load_entities(entities)
        
        stats = dedup.stats()
        self.assertEqual(stats['listings'], 2)
        self.assertEqual(stats['offices'], 1)  # Only one complete office
        self.assertEqual(stats['agents'], 1)   # Only one complete agent
    
    def test_load_detects_duplicates(self):
        """Test that loading works for duplicate detection."""
        dedup = Deduplicator()
        
        entities = [
            {
                'listing_url': 'https://www.sahibinden.com/ilan/1',
                'office_name': 'OFFICE1',
                'agent_name': 'AGENT1',
                'phone_number': '+905321111111',
            },
        ]
        
        dedup.load_entities(entities)
        
        # Check if loaded entity is detected as duplicate
        result = dedup.check_listing(entities[0])
        self.assertFalse(result.is_new)


class TestStatistics(unittest.TestCase):
    """Test cases for deduplicator statistics."""
    
    def test_initial_stats(self):
        """Test that initial stats are empty."""
        dedup = Deduplicator()
        stats = dedup.stats()
        
        self.assertEqual(stats['listings'], 0)
        self.assertEqual(stats['offices'], 0)
        self.assertEqual(stats['agents'], 0)
    
    def test_stats_after_additions(self):
        """Test stats update after adding entities."""
        dedup = Deduplicator()
        
        dedup.add_listing('https://www.sahibinden.com/ilan/1')
        dedup.add_listing('https://www.sahibinden.com/ilan/2')
        dedup.add_office('OFFICE1', '+905321111111')
        dedup.add_agent('AGENT1', '+905321111111')
        
        stats = dedup.stats()
        self.assertEqual(stats['listings'], 2)
        self.assertEqual(stats['offices'], 1)
        self.assertEqual(stats['agents'], 1)
    
    def test_clear(self):
        """Test clearing deduplicator."""
        dedup = Deduplicator()
        
        dedup.add_listing('https://www.sahibinden.com/ilan/1')
        dedup.add_office('OFFICE1', '+905321111111')
        dedup.add_agent('AGENT1', '+905321111111')
        
        stats_before = dedup.stats()
        self.assertGreater(stats_before['listings'], 0)
        
        dedup.clear()
        
        stats_after = dedup.stats()
        self.assertEqual(stats_after['listings'], 0)
        self.assertEqual(stats_after['offices'], 0)
        self.assertEqual(stats_after['agents'], 0)


class TestDeduplicationResult(unittest.TestCase):
    """Test cases for DeduplicationResult dataclass."""
    
    def test_result_new_entity(self):
        """Test DeduplicationResult for new entity."""
        result = DeduplicationResult(
            is_new=True,
            dedupe_key='test-key',
            reason='Test reason'
        )
        
        self.assertTrue(result.is_new)
        self.assertEqual(result.dedupe_key, 'test-key')
        self.assertEqual(result.reason, 'Test reason')
    
    def test_result_duplicate_entity(self):
        """Test DeduplicationResult for duplicate entity."""
        result = DeduplicationResult(
            is_new=False,
            dedupe_key='test-key',
            reason='Already seen'
        )
        
        self.assertFalse(result.is_new)
        self.assertEqual(result.dedupe_key, 'test-key')
        self.assertIn('seen', result.reason.lower())


class TestDeterministicBehavior(unittest.TestCase):
    """Test cases to ensure deterministic, repeatable behavior."""
    
    def test_same_input_same_output(self):
        """Test that same input always produces same decision."""
        data = {
            'office_name': 'EV GAYRIMENKUL',
            'phone_number': '+905321234567'
        }
        
        dedup = Deduplicator()
        
        # Check multiple times
        result1 = dedup.check_office(data)
        result2 = dedup.check_office(data)
        result3 = dedup.check_office(data)
        
        # All should have same result
        self.assertEqual(result1.is_new, result2.is_new)
        self.assertEqual(result2.is_new, result3.is_new)
        self.assertEqual(result1.dedupe_key, result2.dedupe_key)
        self.assertEqual(result2.dedupe_key, result3.dedupe_key)
    
    def test_no_fuzzy_matching(self):
        """Test that similar but different entities are treated as different."""
        dedup = Deduplicator()
        
        # These are similar but should NOT match
        dedup.add_office('EV GAYRIMENKUL', '+905321234567')
        
        similar_entities = [
            {'office_name': 'EV GAYRİMENKUL', 'phone_number': '+905321234567'},  # Different casing
            {'office_name': 'EV GAYRIMENKUL ', 'phone_number': '+905321234567'},  # Trailing space
            {'office_name': 'EV GAYRIMENKUL', 'phone_number': '+90 532 123 4567'},  # Different phone format
            {'office_name': 'EV GAYRIMENKUL', 'phone_number': '+905321234566'},  # Off by one digit
        ]
        
        # All should be treated as NEW (no fuzzy matching)
        for entity in similar_entities:
            result = dedup.check_office(entity)
            self.assertTrue(result.is_new, f"Entity {entity} should be NEW")


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
