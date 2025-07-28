import json
from collections import defaultdict

def check_duplicate_urls():
    """Check for duplicate URLs in the catalog."""
    print("🔍 Checking for duplicate URLs...")
    
    # Load catalog
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data['products']
    
    # Group products by URL
    url_to_products = defaultdict(list)
    
    for product in products:
        url = product.get('url', '').strip()
        if url:
            url_to_products[url].append(product)
    
    # Find duplicates
    duplicates = {url: prods for url, prods in url_to_products.items() if len(prods) > 1}
    
    print(f"📊 Results:")
    print(f"   Total products: {len(products)}")
    print(f"   Products with URLs: {len([p for p in products if p.get('url')])}")
    print(f"   Unique URLs: {len(url_to_products)}")
    print(f"   Duplicate URLs: {len(duplicates)}")
    
    if duplicates:
        print(f"\n❌ Found {len(duplicates)} URLs used by multiple products:")
        
        for i, (url, prods) in enumerate(list(duplicates.items())[:10]):  # Show first 10
            print(f"\n{i+1}. URL: {url[:60]}...")
            print(f"   Used by {len(prods)} products:")
            for j, prod in enumerate(prods):
                print(f"      {j+1}. {prod['name'][:40]} (SKU: {prod['sku']})")
        
        if len(duplicates) > 10:
            print(f"\n... and {len(duplicates) - 10} more duplicate URLs")
    else:
        print("\n✅ No duplicate URLs found!")
    
    return duplicates

if __name__ == "__main__":
    duplicates = check_duplicate_urls()
