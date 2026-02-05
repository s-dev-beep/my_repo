"""Normalizer Demo - Example usage of data normalization.

This script demonstrates how to use the Normalizer to clean and validate
parsed listing data before storage and deduplication.

The normalizer takes raw output from parsers (which may contain whitespace,
inconsistent casing, various phone formats) and transforms it into a clean,
deterministic, consistent format.

Usage:
    python examples/normalizer_demo.py
"""

from src.core.normalizer import Normalizer


# Example 1: Complete real estate office listing with all fields
OFFICE_LISTING_RAW = {
    'office_name': '  Ev Gayrimenkul  ',
    'agent_name': 'ahmet yılmaz',
    'phone_number': '0532 123 4567',
    'city': 'İSTANBUL',
    'district': 'kadıköy',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456'
}

# Example 2: Private seller with minimal contact info
PRIVATE_SELLER_RAW = {
    'office_name': None,
    'agent_name': 'Mehmet Demir',
    'phone_number': '+90 555 888 99 00',
    'city': 'ankara',
    'district': 'çankaya',
    'listing_url': 'https://www.sahibinden.com/ilan/emlak-konut-satilik-ankara-12345'
}

# Example 3: Minimal listing (very incomplete)
MINIMAL_LISTING_RAW = {
    'office_name': None,
    'agent_name': None,
    'phone_number': None,
    'city': 'İzmir',
    'district': None,
    'listing_url': 'https://www.sahibinden.com/ilan/123'
}

# Example 4: Messy real-world data
MESSY_LISTING_RAW = {
    'office_name': '   Gayrimenkul Danışmanlık Ltd. Şti.   ',
    'agent_name': 'fatma kaplan',
    'phone_number': '0 (532) 123-4567',
    'city': 'bursa',
    'district': '   nilüfer   ',
    'listing_url': 'https://www.sahibinden.com/ilan/gayrimenkul-bursa-456'
}

# Example 5: International phone number
INTERNATIONAL_PHONE_RAW = {
    'office_name': 'Premium Emlak',
    'agent_name': 'Ali Demir',
    'phone_number': '+90 532 123 4567',
    'city': 'Antalya',
    'district': 'Kemer',
    'listing_url': 'https://www.sahibinden.com/ilan/antalya-kemer-789'
}


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def compare_data(label: str, raw: dict, normalized: dict):
    """Print side-by-side comparison of raw and normalized data."""
    print(f"📊 {label}")
    print("-" * 70)
    
    fields = ['office_name', 'agent_name', 'phone_number', 'city', 'district', 'listing_url']
    
    for field in fields:
        raw_val = raw.get(field)
        norm_val = normalized.get(field)
        
        # Format for display
        raw_display = repr(raw_val) if raw_val else "None"
        norm_display = repr(norm_val) if norm_val else "None"
        
        # Highlight changes
        changed = raw_val != norm_val
        marker = "→" if changed else " "
        
        print(f"{marker} {field:15} | {raw_display:30} → {norm_display}")
    
    # Show metadata
    print(f"\n  Source: {normalized.get('source')}")
    print(f"  Confidence: {normalized.get('confidence')}")
    print()


def demo_basic_normalization():
    """Demonstrate normalization of office listing."""
    print_section("DEMO 1: Office Listing with All Fields")
    
    normalizer = Normalizer()
    normalized = normalizer.normalize(OFFICE_LISTING_RAW)
    
    compare_data("Complete office listing", OFFICE_LISTING_RAW, normalized)
    
    # Validate
    is_valid = normalizer.validate(normalized)
    print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}\n")


def demo_private_seller():
    """Demonstrate normalization of private seller listing."""
    print_section("DEMO 2: Private Seller with International Phone")
    
    normalizer = Normalizer()
    normalized = normalizer.normalize(PRIVATE_SELLER_RAW)
    
    compare_data("Private seller", PRIVATE_SELLER_RAW, normalized)
    
    is_valid = normalizer.validate(normalized)
    print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}\n")


def demo_minimal_listing():
    """Demonstrate handling of very incomplete listing."""
    print_section("DEMO 3: Minimal Listing (Low Confidence)")
    
    normalizer = Normalizer()
    normalized = normalizer.normalize(MINIMAL_LISTING_RAW)
    
    compare_data("Minimal listing", MINIMAL_LISTING_RAW, normalized)
    
    is_valid = normalizer.validate(normalized)
    print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}\n")
    print(f"⚠️  Low confidence score indicates incomplete data\n")


def demo_messy_data():
    """Demonstrate handling of messy real-world data."""
    print_section("DEMO 4: Messy Real-World Data")
    
    normalizer = Normalizer()
    normalized = normalizer.normalize(MESSY_LISTING_RAW)
    
    compare_data("Messy data with whitespace and mixed casing", MESSY_LISTING_RAW, normalized)
    
    is_valid = normalizer.validate(normalized)
    print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}\n")


def demo_phone_normalization():
    """Demonstrate phone number normalization."""
    print_section("DEMO 5: Phone Number Normalization")
    
    normalizer = Normalizer()
    normalized = normalizer.normalize(INTERNATIONAL_PHONE_RAW)
    
    compare_data("International phone format", INTERNATIONAL_PHONE_RAW, normalized)
    
    is_valid = normalizer.validate(normalized)
    print(f"✓ Validation: {'PASSED' if is_valid else 'FAILED'}\n")
    
    # Explain phone normalization
    print("📞 Phone Normalization Details:")
    print("-" * 70)
    print(f"Input format: +90 532 123 4567")
    print(f"  - '+90' is the Turkey country code")
    print(f"  - Spaces and dashes are removed")
    print(f"Output format (E.164): +905321234567")
    print(f"  - International standard format")
    print(f"  - 13 characters total: +90 (3) + 10 digits")
    print(f"  - Deterministic and consistent\n")


def demo_confidence_scores():
    """Demonstrate confidence scoring."""
    print_section("DEMO 6: Confidence Scoring")
    
    print("How confidence is calculated:")
    print("-" * 70)
    print("HIGH confidence (4 points):")
    print("  - office_name present")
    print("  - agent_name present")
    print("  - phone_number present")
    print("  - city AND district present\n")
    
    print("MEDIUM confidence (2-3 points):")
    print("  - At least 2 contact fields present\n")
    
    print("LOW confidence (0-1 points):")
    print("  - Very little information\n")
    
    normalizer = Normalizer()
    
    examples = [
        ("✓ HIGH - All fields", OFFICE_LISTING_RAW),
        ("◐ MEDIUM - Office + Phone + Location", PRIVATE_SELLER_RAW),
        ("✗ LOW - Location only", MINIMAL_LISTING_RAW),
    ]
    
    for label, raw_data in examples:
        normalized = normalizer.normalize(raw_data)
        confidence = normalized['confidence']
        print(f"{label:30} → Confidence: {confidence}")
    
    print()


def demo_deterministic_normalization():
    """Demonstrate that normalization is deterministic."""
    print_section("DEMO 7: Deterministic Normalization")
    
    print("The same input should always produce the same output.")
    print("This is crucial for deduplication.\n")
    
    normalizer = Normalizer()
    
    # Normalize the same data multiple times
    results = []
    for i in range(3):
        normalized = normalizer.normalize(OFFICE_LISTING_RAW)
        results.append(normalized)
    
    # Check all results are identical
    all_same = all(r == results[0] for r in results)
    
    print(f"Run 1: {results[0]}")
    print()
    print(f"Run 2: {results[1]}")
    print()
    print(f"Run 3: {results[2]}")
    print()
    print(f"All results identical: {'✓ YES' if all_same else '✗ NO'}\n")
    
    print("Deterministic normalization means:")
    print("- Same input → Same output (always)")
    print("- Deduplication can compare hashes reliably")
    print("- No random elements or timestamps in normalization\n")


def demo_validation():
    """Demonstrate validation of normalized data."""
    print_section("DEMO 8: Data Validation")
    
    normalizer = Normalizer()
    
    print("Valid normalized data:")
    print("-" * 70)
    normalized = normalizer.normalize(OFFICE_LISTING_RAW)
    is_valid = normalizer.validate(normalized)
    print(f"Result: {'✓ VALID' if is_valid else '✗ INVALID'}\n")
    
    print("Invalid data (missing field):")
    print("-" * 70)
    invalid_data = {
        'office_name': 'EV GAYRIMENKUL',
        'agent_name': 'AHMET YILMAZ',
        'phone_number': '+905321234567',
        'city': 'Istanbul',
        # Missing: district, listing_url, source, confidence
    }
    is_valid = normalizer.validate(invalid_data)
    print(f"Result: {'✓ VALID' if is_valid else '✗ INVALID'}\n")
    
    print("Invalid data (phone in wrong format):")
    print("-" * 70)
    invalid_phone = {
        'office_name': 'EV GAYRIMENKUL',
        'agent_name': 'AHMET YILMAZ',
        'phone_number': '0532 123 4567',  # Not E.164 format!
        'city': 'Istanbul',
        'district': 'Kadikoy',
        'listing_url': 'https://...',
        'source': 'sahibinden',
        'confidence': 'high'
    }
    is_valid = normalizer.validate(invalid_phone)
    print(f"Result: {'✓ VALID' if is_valid else '✗ INVALID'}\n")


def demo_edge_cases():
    """Demonstrate handling of edge cases."""
    print_section("DEMO 9: Edge Cases")
    
    normalizer = Normalizer()
    
    print("Edge Case 1: Empty strings should become None")
    print("-" * 70)
    edge_case_1 = {
        'office_name': '   ',  # Only whitespace
        'agent_name': '',      # Empty string
        'phone_number': None,
        'city': 'Istanbul',
        'district': 'Fatih',
        'listing_url': 'https://example.com/123'
    }
    normalized = normalizer.normalize(edge_case_1)
    print(f"Input office_name: {repr(edge_case_1['office_name'])}")
    print(f"Output office_name: {repr(normalized['office_name'])}")
    print(f"Input agent_name: {repr(edge_case_1['agent_name'])}")
    print(f"Output agent_name: {repr(normalized['agent_name'])}\n")
    
    print("Edge Case 2: Invalid phone formats are ignored")
    print("-" * 70)
    edge_case_2 = {
        'office_name': 'TEST OFFICE',
        'agent_name': 'TEST AGENT',
        'phone_number': '1234567890',  # Too short, invalid
        'city': 'Istanbul',
        'district': 'Beyoglu',
        'listing_url': 'https://example.com/456'
    }
    normalized = normalizer.normalize(edge_case_2)
    print(f"Input phone_number: {repr(edge_case_2['phone_number'])}")
    print(f"Output phone_number: {repr(normalized['phone_number'])}")
    print("→ Invalid phone numbers become None (not guessed)\n")
    
    print("Edge Case 3: No data enrichment occurs")
    print("-" * 70)
    edge_case_3 = {
        'office_name': None,
        'agent_name': 'Unknown Agent',
        'phone_number': None,
        'city': None,
        'district': None,
        'listing_url': 'https://example.com/789'
    }
    normalized = normalizer.normalize(edge_case_3)
    print(f"Input: Minimal data (no city/district)")
    print(f"Output: {normalized['city']}, {normalized['district']}")
    print("→ Missing data stays None (no guessing, no enrichment)\n")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  NORMALIZER DEMO - Data Normalization & Validation".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    demo_basic_normalization()
    demo_private_seller()
    demo_minimal_listing()
    demo_messy_data()
    demo_phone_normalization()
    demo_confidence_scores()
    demo_deterministic_normalization()
    demo_validation()
    demo_edge_cases()
    
    print_section("Summary")
    print("""
The Normalizer provides:

1. NAME NORMALIZATION
   - Trim whitespace
   - Convert to UPPERCASE
   - Deterministic and consistent

2. PHONE NORMALIZATION
   - Extract from various formats (0XXX, +90, spaces, dashes)
   - Normalize to E.164 format: +905XXXXXXXXX
   - Return None if invalid (no guessing)

3. LOCATION NORMALIZATION
   - Trim whitespace
   - Title case (first letter capitalized)
   - No modification beyond casing/trimming

4. CONFIDENCE SCORING
   - HIGH: 4+ contact fields
   - MEDIUM: 2-3 contact fields
   - LOW: 0-1 contact fields

5. VALIDATION
   - Check all required fields exist
   - Check phone format (E.164)
   - Check confidence is valid enum

Next step: Deduplication uses normalized data for comparison.
""")


if __name__ == '__main__':
    main()
