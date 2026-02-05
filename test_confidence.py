"""Quick test to see normalized confidence levels"""
from src.adapters.sahibinden.parser import SahibindenParser
from src.core.normalizer import Normalizer
import json

html = """
<html><body>
<nav class="breadcrumb">
    <ul><li>Türkiye</li><li>İstanbul</li><li>Beşiktaş</li><li>Kiralık Daire</li></ul>
</nav>
<div class="classifiedInfo">
    <div class="classifiedInfoCell">
        <span class="name">Etap Gayrimenkul</span>
        <span class="userName">Ahmet Kaya</span>
        <button title="Telefon">+90 212 234 5678</button>
    </div>
</div>
<h1>2+1 Daire, 85 m², Merkez</h1>
</body></html>
"""

parser = SahibindenParser()
normalizer = Normalizer()

parsed = parser.parse_listing_page(html, "https://www.sahibinden.com/test")
print("PARSED:")
print(json.dumps(parsed, indent=2, default=str))
print()

normalized = normalizer.normalize(parsed)
print("NORMALIZED:")
print(json.dumps(normalized, indent=2, default=str))
