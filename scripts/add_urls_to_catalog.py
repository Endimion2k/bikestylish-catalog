#!/usr/bin/env python3
"""
Add URLs to existing product catalog.
"""

import json
import re
from typing import Dict, List, Optional

def parse_sitemap_urls(sitemap_file: str) -> List[str]:
    """Parse the sitemap XML and extract product URLs."""
    urls = []
    
    try:
        # Read the file content
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all CDATA URLs
        cdata_pattern = r'<!\[CDATA\[\s*(https://www\.bikestylish\.ro/[^]]+)\s*\]\]>'
        matches = re.findall(cdata_pattern, content)
        
        for url in matches:
            url = url.strip()
            if url and ('piese' in url or 'accesorii' in url or 'biciclet' in url):
                urls.append(url)
                
    except Exception as e:
        print(f"Error parsing sitemap: {e}")
        
    return urls

def match_url_to_product_name(url: str, product_name: str) -> float:
    """Calculate similarity score between URL and product name."""
    if not url or not product_name:
        return 0.0
    
    # Extract filename from URL
    filename = url.split('/')[-1].replace('.html', '')
    filename_clean = re.sub(r'[^\w\s-]', ' ', filename.lower())
    filename_words = set(w for w in filename_clean.split() if len(w) > 2)
    
    # Clean product name
    product_clean = re.sub(r'[^\w\s-]', ' ', product_name.lower())
    product_words = set(w for w in product_clean.split() if len(w) > 2)
    
    if not filename_words or not product_words:
        return 0.0
    
    # Calculate overlap
    common_words = filename_words.intersection(product_words)
    score = len(common_words) / max(len(filename_words), len(product_words))
    
    return score

def add_urls_to_catalog():
    """Add URLs to existing product catalog."""
    print("🔄 Loading existing catalog...")
    
    # Load existing catalog
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    print(f"📦 Loaded {len(catalog['products'])} products")
    
    # Load URLs
    print("🔄 Parsing sitemap URLs...")
    urls = parse_sitemap_urls('../../link.txt')
    print(f"🔗 Found {len(urls)} URLs")
    
    # Match URLs to products
    print("🔄 Matching URLs to products...")
    matched_count = 0
    
    for i, product in enumerate(catalog['products']):
        if i % 500 == 0:
            print(f"   Processed {i}/{len(catalog['products'])} products...")
        
        best_url = ""
        best_score = 0.0
        
        # Try to match with URLs (sample first 100 URLs for efficiency)
        for url in urls[:min(1000, len(urls))]:  # Limit to first 1000 URLs for speed
            score = match_url_to_product_name(url, product['name'])
            if score > best_score and score > 0.3:
                best_score = score
                best_url = url
        
        # Add URL to product
        product['url'] = best_url
        if best_url:
            matched_count += 1
    
    print(f"✅ Matched {matched_count} products with URLs")
    
    # Update catalog metadata
    catalog['last_updated'] = "2025-07-28T22:30:00.000000"
    
    # Save updated catalog
    with open('../data/products.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print("✅ Updated catalog saved!")
    
    # Show sample with URLs
    products_with_urls = [p for p in catalog['products'] if p.get('url')]
    print(f"\n📋 Sample products with URLs ({len(products_with_urls)} total):")
    for i, product in enumerate(products_with_urls[:5]):
        print(f"   {i+1}. {product['name']}")
        print(f"      URL: {product['url']}")

if __name__ == "__main__":
    add_urls_to_catalog()
