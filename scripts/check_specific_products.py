import json

# Load catalog
with open('../data/products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

products = data['products']

# Find the specific products mentioned
roti_products = [p for p in products if 'roti ajutatoare' in p['name'].lower()]

print("🔍 Verificare produse 'roti ajutatoare':")
print(f"Găsite {len(roti_products)} produse:")

for product in roti_products:
    print(f"\n• SKU {product['sku']}: {product['name']}")
    print(f"  Preț: {product['price']} RON")
    print(f"  URL: {product.get('url', 'No URL')}")

# Check if the specific SKUs from the example have unique URLs
specific_skus = ['100015', '100016']
print(f"\n🎯 Verificare SKU-uri specifice din exemplu:")

for sku in specific_skus:
    product = next((p for p in products if p['sku'] == sku), None)
    if product:
        print(f"\n• SKU {sku}: {product['name']}")
        print(f"  Preț: {product['price']} RON") 
        print(f"  URL: {product.get('url', 'No URL')}")
    else:
        print(f"\n• SKU {sku}: Nu a fost găsit")

print(f"\n📊 Statistici finale:")
print(f"Total produse: {len(products)}")
print(f"Produse cu URL-uri: {len([p for p in products if p.get('url')])}")
print(f"URL-uri unice: {len(set(p['url'] for p in products if p.get('url')))}")
