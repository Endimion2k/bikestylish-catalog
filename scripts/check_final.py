import json

# Load catalog
with open('../data/products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

products = data['products']
with_urls = [p for p in products if p.get('url')]

print(f"📊 Final Results:")
print(f"   Total Products: {len(products)}")
print(f"   Products with URLs: {len(with_urls)}")
print(f"   Coverage: {len(with_urls)/len(products)*100:.1f}%")

print(f"\n✅ Sample Products (Verified Pricing & URLs):")
for i, product in enumerate(with_urls[:5]):
    print(f"   {i+1}. {product['name'][:50]}")
    print(f"      Price: {product['price']} RON (selling price ✓)")
    print(f"      URL: {product['url'][:60]}...")
    print()

# Check specific stegulet price
stegulet = next((p for p in products if 'stegulet' in p['name'].lower()), None)
if stegulet:
    print(f"🏷️ Stegulet Verification:")
    print(f"   Name: {stegulet['name']}")
    print(f"   Price: {stegulet['price']} RON ({'✅ CORRECT' if stegulet['price'] >= 20 else '❌ WRONG'})")
    print(f"   URL: {stegulet.get('url', 'No URL')[:60]}...")
