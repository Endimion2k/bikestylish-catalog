#!/usr/bin/env python3
"""
Fast URL matching for BikeStylish catalog.
"""

import json
import re
from typing import Dict, List
import time

def fast_url_match():
    """Quick URL matching for products."""
    print("🚀 Fast URL matching started...")
    
    # Load products
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    products = catalog['products']
    print(f"📦 Processing {len(products)} products")
    
    # Load URLs and create simple mapping
    urls = []
    try:
        with open('../../link.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract URLs from CDATA
        cdata_pattern = r'<!\[CDATA\[\s*(https://www\.bikestylish\.ro/[^]]+)\s*\]\]>'
        urls = re.findall(cdata_pattern, content)
        print(f"🔗 Found {len(urls)} URLs")
        
        # Create URL lookup by keywords
        url_keywords = {}
        for url in urls:
            filename = url.split('/')[-1].replace('.html', '').lower()
            keywords = re.findall(r'\w+', filename)
            for keyword in keywords:
                if len(keyword) > 3:
                    if keyword not in url_keywords:
                        url_keywords[keyword] = []
                    url_keywords[keyword].append(url)
        
        print(f"📝 Created keyword index with {len(url_keywords)} entries")
        
    except Exception as e:
        print(f"❌ Error loading URLs: {e}")
        return
    
    # Match products to URLs
    matched = 0
    for i, product in enumerate(products):
        if i % 1000 == 0:
            print(f"   Progress: {i}/{len(products)} ({matched} matched)")
        
        # Quick keyword matching
        product_words = re.findall(r'\w+', product['name'].lower())
        best_url = ""
        
        for word in product_words:
            if len(word) > 3 and word in url_keywords:
                # Take first matching URL
                best_url = url_keywords[word][0]
                break
        
        product['url'] = best_url
        if best_url:
            matched += 1
    
    print(f"✅ Matched {matched}/{len(products)} products with URLs")
    
    # Save updated catalog
    catalog['last_updated'] = time.strftime("%Y-%m-%dT%H:%M:%S.000000")
    
    with open('../data/products.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print("💾 Catalog saved with URLs!")
    
    # Show samples
    with_urls = [p for p in products if p.get('url')]
    print(f"\n📋 Sample products with URLs ({len(with_urls)} total):")
    for product in with_urls[:3]:
        print(f"   • {product['name']}")
        print(f"     {product['url']}")

if __name__ == "__main__":
    fast_url_match()
