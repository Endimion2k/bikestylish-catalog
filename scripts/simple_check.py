print("Starting verification...")

import json

with open('../data/products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

products = data['products']
with_urls = [p for p in products if p.get('url') and p['url'].strip()]

print(f"Total products: {len(products)}")
print(f"Products with URLs: {len(with_urls)}")

# Check for duplicates
url_counts = {}
for p in with_urls:
    url = p['url'].strip()
    url_counts[url] = url_counts.get(url, 0) + 1

duplicates = {url: count for url, count in url_counts.items() if count > 1}
print(f"Duplicate URLs: {len(duplicates)}")

# Find some products that got URLs based on name similarity
print("\nSample products with URLs:")
for i, p in enumerate(with_urls[:5]):
    print(f"{i+1}. {p['name'][:45]}")
    print(f"   URL: {p['url'][:60]}...")

print("Verification complete.")
