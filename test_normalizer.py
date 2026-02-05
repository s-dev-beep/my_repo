#!/usr/bin/env python3
"""Quick test of normalizer functionality."""

from src.core.normalizer import Normalizer

def test_basic_normalization():
    """Test basic normalization."""
    normalizer = Normalizer()
    
    raw = {
        'office_name': '  Ev Gayrimenkul  ',
        'agent_name': 'ahmet yılmaz',
        'phone_number': '0532 123 4567',
        'city': 'İSTANBUL',
        'district': 'kadıköy',
        'listing_url': 'https://www.sahibinden.com/ilan/test'
    }
    
    result = normalizer.normalize(raw)
    
    assert result['office_name'] == 'EV GAYRIMENKUL'
    assert result['agent_name'] == 'AHMET YILMAZ'
    assert result['phone_number'] == '+905321234567'
    assert result['city'] == 'İstanbul'
    assert result['district'] == 'Kadıköy'
    assert result['source'] == 'sahibinden'
    assert result['confidence'] == 'high'
    assert normalizer.validate(result) == True
    
    print("✓ Test 1: Basic normalization PASSED")


def test_private_seller():
    """Test private seller with less data."""
    normalizer = Normalizer()
    
    raw = {
        'office_name': None,
        'agent_name': 'mehmet',
        'phone_number': None,
        'city': 'ankara',
        'district': 'çankaya',
        'listing_url': 'https://www.sahibinden.com/ilan/test2'
    }
    
    result = normalizer.normalize(raw)
    
    assert result['office_name'] is None
    assert result['agent_name'] == 'MEHMET'
    assert result['phone_number'] is None
    assert result['city'] == 'Ankara'
    assert result['district'] == 'Çankaya'
    assert result['confidence'] == 'medium'
    assert normalizer.validate(result) == True
    
    print("✓ Test 2: Private seller PASSED")


def test_invalid_phone():
    """Test that invalid phones return None."""
    normalizer = Normalizer()
    
    test_cases = [
        '1234567890',           # Too short
        'not a phone',          # Invalid
        '0532 123 45',          # Too short
        '+33612345678',         # France
    ]
    
    for phone in test_cases:
        raw = {
            'office_name': 'TEST',
            'agent_name': 'TEST',
            'phone_number': phone,
            'city': 'Istanbul',
            'district': 'Fatih',
            'listing_url': 'https://example.com/test'
        }
        result = normalizer.normalize(raw)
        assert result['phone_number'] is None, f"Expected None for {phone}"
    
    print("✓ Test 3: Invalid phones return None PASSED")


def test_deterministic():
    """Test deterministic normalization."""
    normalizer = Normalizer()
    
    raw = {
        'office_name': '  test  ',
        'agent_name': 'john',
        'phone_number': '0532 123 4567',
        'city': 'istanbul',
        'district': 'fatih',
        'listing_url': 'https://sahibinden.com/test'
    }
    
    result1 = normalizer.normalize(raw)
    result2 = normalizer.normalize(raw)
    result3 = normalizer.normalize(raw)
    
    assert result1 == result2 == result3, "Normalization is not deterministic"
    
    print("✓ Test 4: Deterministic normalization PASSED")


def test_valid_phones():
    """Test various valid phone formats."""
    normalizer = Normalizer()
    
    test_cases = [
        ('0532 123 4567', '+905321234567'),
        ('+90 532 123 4567', '+905321234567'),
        ('05321234567', '+905321234567'),
        ('+905321234567', '+905321234567'),
        ('0 (532) 123-4567', '+905321234567'),
    ]
    
    for input_phone, expected in test_cases:
        raw = {
            'office_name': 'TEST',
            'agent_name': 'TEST',
            'phone_number': input_phone,
            'city': 'Istanbul',
            'district': 'Fatih',
            'listing_url': 'https://example.com/test'
        }
        result = normalizer.normalize(raw)
        assert result['phone_number'] == expected, f"Phone {input_phone} -> {result['phone_number']}, expected {expected}"
    
    print("✓ Test 5: Valid phone formats PASSED")


if __name__ == '__main__':
    test_basic_normalization()
    test_private_seller()
    test_invalid_phone()
    test_deterministic()
    test_valid_phones()
    print("\n✅ All tests PASSED!")
