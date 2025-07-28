import json

try:
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data['products']
    with_urls = [p for p in products if p.get('url')]
    
    print(f"📊 Current status:")
    print(f"Total products: {len(products)}")
    print(f"Products with URLs: {len(with_urls)}")
    
    # Check for duplicates
    urls_list = [p['url'] for p in with_urls]
    unique_urls = len(set(urls_list))
    
    print(f"Unique URLs: {unique_urls}")
    print(f"Duplicates: {len(urls_list) - unique_urls}")
    
    # Check specific products
    roti_products = [p for p in products if 'roti ajutatoare' in p['name'].lower()]
    print(f"\n🎯 Roti ajutatoare products:")
    for product in roti_products[:3]:
        print(f"   • {product['name'][:40]}")
        print(f"     URL: {product.get('url', 'No URL')[:50]}...")
        
except Exception as e:
    print(f"Error: {e}")
