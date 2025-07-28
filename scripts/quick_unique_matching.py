import json
import re
from collections import defaultdict
from typing import Dict, Set
import time

def quick_unique_url_matching():
    """Quick URL matching that ensures no duplicates."""
    print("🚀 Quick unique URL matching...")
    
    # Load catalog
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data['products']
    print(f"📦 Processing {len(products)} products")
    
    # Load URLs and create keyword index
    url_keywords = {}
    used_urls = set()
    
    try:
        with open('../../link.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract URLs
        cdata_pattern = r'<!\[CDATA\[\s*(https://www\.bikestylish\.ro/[^]]+)\s*\]\]>'
        urls = re.findall(cdata_pattern, content)
        print(f"🔗 Found {len(urls)} URLs")
        
        # Create keyword index for faster matching
        for url in urls:
            filename = url.split('/')[-1].replace('.html', '').lower()
            keywords = re.findall(r'\w+', filename)
            for keyword in keywords:
                if len(keyword) > 3:
                    if keyword not in url_keywords:
                        url_keywords[keyword] = []
                    url_keywords[keyword].append(url)
        
        print(f"📝 Created keyword index")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Reset URLs and match
    matched = 0
    
    # Sort products by price (higher price gets priority)
    products_sorted = sorted(products, key=lambda p: p.get('price', 0), reverse=True)
    
    for i, product in enumerate(products_sorted):
        if i % 1000 == 0:
            print(f"   Progress: {i}/{len(products_sorted)} ({matched} matched)")
        
        # Reset URL
        product['url'] = ""
        
        # Find matching URL that hasn't been used
        product_words = re.findall(r'\w{4,}', product['name'].lower())
        found_url = ""
        
        for word in product_words:
            if word in url_keywords:
                # Find first unused URL for this keyword
                for url in url_keywords[word]:
                    if url not in used_urls:
                        found_url = url
                        break
                if found_url:
                    break
        
        # Assign URL if found
        if found_url:
            product['url'] = found_url
            used_urls.add(found_url)
            matched += 1
    
    print(f"✅ Matched {matched}/{len(products)} products with unique URLs")
    
    # Save updated catalog
    data['last_updated'] = time.strftime("%Y-%m-%dT%H:%M:%S.000000")
    
    with open('../data/products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("💾 Catalog saved!")
    
    # Verify no duplicates
    url_counts = defaultdict(int)
    for product in products:
        url = product.get('url', '').strip()
        if url:
            url_counts[url] += 1
    
    duplicates = sum(1 for count in url_counts.values() if count > 1)
    
    print(f"🔍 Verification: {duplicates} duplicate URLs found")
    
    # Show samples
    with_urls = [p for p in products if p.get('url')]
    print(f"\n📋 Sample results ({len(with_urls)} total with URLs):")
    for product in with_urls[:3]:
        print(f"   • {product['name'][:40]} - {product['price']} RON")
        print(f"     {product['url'][:60]}...")

if __name__ == "__main__":
    quick_unique_url_matching()
