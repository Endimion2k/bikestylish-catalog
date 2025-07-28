import json
import re
from collections import defaultdict
from typing import Dict, List, Set

def improved_url_matching():
    """Improved URL matching algorithm that avoids duplicates."""
    print("🔄 Starting improved URL matching (avoiding duplicates)...")
    
    # Load catalog
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data['products']
    print(f"📦 Processing {len(products)} products")
    
    # Load URLs
    urls = []
    try:
        with open('../../link.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract URLs from CDATA
        cdata_pattern = r'<!\[CDATA\[\s*(https://www\.bikestylish\.ro/[^]]+)\s*\]\]>'
        urls = re.findall(cdata_pattern, content)
        print(f"🔗 Found {len(urls)} URLs from sitemap")
        
    except Exception as e:
        print(f"❌ Error loading URLs: {e}")
        return
    
    # Create better scoring for URL-product matching
    def calculate_detailed_score(url: str, product: Dict) -> float:
        """Calculate detailed similarity score between URL and product."""
        if not url or not product.get('name'):
            return 0.0
        
        # Extract filename from URL
        filename = url.split('/')[-1].replace('.html', '').lower()
        filename_words = set(re.findall(r'\w+', filename))
        
        # Product details
        product_name = product['name'].lower()
        product_words = set(re.findall(r'\w+', product_name))
        brand = product.get('brand', '').lower()
        sku = product.get('sku', '').lower()
        
        if not filename_words or not product_words:
            return 0.0
        
        # Calculate word overlap
        common_words = filename_words.intersection(product_words)
        base_score = len(common_words) / max(len(filename_words), len(product_words))
        
        # Bonus for brand match
        if brand and any(brand in word for word in filename_words):
            base_score += 0.2
        
        # Bonus for SKU match (if present in URL)
        if sku and sku in filename:
            base_score += 0.3
        
        # Penalty for generic terms
        generic_terms = {'bicicleta', 'accesorii', 'piese', 'bike', 'cycling'}
        if filename_words.intersection(generic_terms) and len(common_words) <= 1:
            base_score *= 0.5
        
        return min(base_score, 1.0)
    
    # Track used URLs to avoid duplicates
    used_urls: Set[str] = set()
    matched_count = 0
    
    # Reset all URLs first
    for product in products:
        product['url'] = ""
    
    # Sort products by importance (higher price = more important)
    products_sorted = sorted(products, key=lambda p: p.get('price', 0), reverse=True)
    
    print("🔄 Matching URLs to products (avoiding duplicates)...")
    
    for i, product in enumerate(products_sorted):
        if i % 1000 == 0:
            print(f"   Progress: {i}/{len(products_sorted)} ({matched_count} matched)")
        
        best_url = ""
        best_score = 0.0
        
        # Find best available URL for this product
        for url in urls:
            if url in used_urls:
                continue  # Skip already used URLs
                
            score = calculate_detailed_score(url, product)
            if score > best_score and score > 0.4:  # Higher threshold
                best_score = score
                best_url = url
        
        # Assign URL if found
        if best_url:
            product['url'] = best_url
            used_urls.add(best_url)
            matched_count += 1
    
    print(f"✅ Matched {matched_count}/{len(products)} products with unique URLs")
    
    # Update catalog metadata
    data['last_updated'] = "2025-07-28T22:35:00.000000"
    
    # Save updated catalog
    with open('../data/products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("💾 Updated catalog saved!")
    
    # Verify no duplicates
    url_counts = defaultdict(int)
    for product in products:
        url = product.get('url', '').strip()
        if url:
            url_counts[url] += 1
    
    duplicates = {url: count for url, count in url_counts.items() if count > 1}
    
    if duplicates:
        print(f"❌ Still found {len(duplicates)} duplicate URLs!")
        for url, count in list(duplicates.items())[:5]:
            print(f"   {url[:50]}... used {count} times")
    else:
        print("✅ No duplicate URLs found!")
    
    # Show sample results
    with_urls = [p for p in products if p.get('url')]
    print(f"\n📋 Sample matched products ({len(with_urls)} total with URLs):")
    for product in with_urls[:5]:
        print(f"   • {product['name'][:40]}")
        print(f"     URL: {product['url'][:60]}...")

if __name__ == "__main__":
    improved_url_matching()
