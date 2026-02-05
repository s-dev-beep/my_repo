"""Parser Demo - Example usage of the HTML parsing functionality.

This script demonstrates how to use the Sahibinden parser to extract
structured data from raw HTML content.

Usage:
    python examples/parser_demo.py
"""

from src.adapters.sahibinden.parser import SahibindenParser


# Example HTML snippets (simplified for demonstration)
# In production, this would come from the Fetcher

EXAMPLE_HTML_WITH_OFFICE = """
<!DOCTYPE html>
<html>
<head><title>Kiralık Daire - Sahibinden.com</title></head>
<body>
    <div class="breadcrumb">
        <ul>
            <li>Anasayfa</li>
            <li>İlan</li>
            <li>Emlak</li>
            <li>Konut</li>
            <li>İstanbul</li>
            <li>Kadıköy</li>
            <li>Moda Mahallesi</li>
        </ul>
    </div>
    
    <div class="classifiedInfo">
        <div class="classifiedInfoCell">
            <span class="name">Ev Gayrimenkul</span>
            <span class="userName">Ahmet Yılmaz</span>
            <div>Telefon: 0532 123 45 67</div>
        </div>
    </div>
</body>
</html>
"""

EXAMPLE_HTML_PRIVATE_SELLER = """
<!DOCTYPE html>
<html>
<head><title>Satılık Daire - Sahibinden.com</title></head>
<body>
    <div class="breadcrumb">
        <ul>
            <li>Anasayfa</li>
            <li>İlan</li>
            <li>Emlak</li>
            <li>Ankara</li>
            <li>Çankaya</li>
        </ul>
    </div>
    
    <div class="classifiedInfo">
        <div class="classifiedInfoCell">
            <span class="userName">Mehmet Demir</span>
        </div>
    </div>
</body>
</html>
"""

EXAMPLE_HTML_MINIMAL = """
<!DOCTYPE html>
<html>
<head><title>Listing</title></head>
<body>
    <div class="breadcrumb">
        <ul>
            <li>Anasayfa</li>
            <li>Emlak</li>
            <li>İzmir</li>
        </ul>
    </div>
</body>
</html>
"""


def demo_basic_parsing():
    """Demonstrate basic parsing with all fields present."""
    print("=" * 60)
    print("DEMO 1: Parsing listing with real estate office")
    print("=" * 60)
    
    parser = SahibindenParser()
    
    # Parse the HTML
    result = parser.parse_listing_page(
        html=EXAMPLE_HTML_WITH_OFFICE,
        url="https://www.sahibinden.com/ilan/emlak-konut-kiralik-istanbul-kadikoy-123456"
    )
    
    print("\n📋 Parsing Result:")
    if result:
        for key, value in result.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key:15} : {value}")
    else:
        print("  ❌ Failed to parse HTML")
    
    print()


def demo_private_seller():
    """Demonstrate parsing a private seller listing (no office)."""
    print("=" * 60)
    print("DEMO 2: Parsing private seller listing (no office)")
    print("=" * 60)
    
    parser = SahibindenParser()
    
    result = parser.parse_listing_page(
        html=EXAMPLE_HTML_PRIVATE_SELLER,
        url="https://www.sahibinden.com/ilan/emlak-konut-satilik-ankara-cankaya-789012"
    )
    
    print("\n📋 Parsing Result:")
    if result:
        for key, value in result.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key:15} : {value}")
    else:
        print("  ❌ Failed to parse HTML")
    
    print()


def demo_minimal_data():
    """Demonstrate parsing with minimal data available."""
    print("=" * 60)
    print("DEMO 3: Parsing with minimal data (only city)")
    print("=" * 60)
    
    parser = SahibindenParser()
    
    result = parser.parse_listing_page(
        html=EXAMPLE_HTML_MINIMAL,
        url="https://www.sahibinden.com/ilan/emlak-konut-izmir-345678"
    )
    
    print("\n📋 Parsing Result:")
    if result:
        for key, value in result.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key:15} : {value}")
    else:
        print("  ❌ Failed to parse HTML")
    
    print()


def demo_integration_example():
    """Show how parser integrates with fetcher (pseudocode)."""
    print("=" * 60)
    print("DEMO 4: Integration with Fetcher (Pseudocode)")
    print("=" * 60)
    
    print("""
    # In production, you would use the parser like this:
    
    from src.core.fetcher import Fetcher
    from src.adapters.sahibinden.parser import SahibindenParser
    
    # Step 1: Fetch HTML
    fetcher = Fetcher()
    url = "https://www.sahibinden.com/ilan/emlak-konut-kiralik/..."
    html = await fetcher.fetch(url)
    
    # Step 2: Parse HTML
    parser = SahibindenParser()
    data = parser.parse_listing_page(html, url)
    
    # Step 3: Save to database
    if data:
        # Save to MongoDB, validate with Pydantic, etc.
        save_to_database(data)
    """)
    print()


def main():
    """Run all demo examples."""
    print("\n🚀 Sahibinden Parser Demo\n")
    
    demo_basic_parsing()
    demo_private_seller()
    demo_minimal_data()
    demo_integration_example()
    
    print("=" * 60)
    print("✅ Demo completed!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  • Parser is stateless and reusable")
    print("  • All fields are optional (None if not found)")
    print("  • City/district ONLY from breadcrumb")
    print("  • Phone numbers may require dynamic extraction")
    print("  • Graceful handling of missing data")
    print()


if __name__ == "__main__":
    main()
