import json
import re
from typing import Dict
import time

def optimized_name_matching():
    """Optimized name-based URL matching."""
    print("⚡ Optimized name-based URL matching...")
    
    # Load catalog
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data['products']
    print(f"📦 Processing {len(products)} products")
    
    # Load URLs
    try:
        with open('../../link.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        cdata_pattern = r'<!\[CDATA\[\s*(https://www\.bikestylish\.ro/[^]]+)\s*\]\]>'
        urls = re.findall(cdata_pattern, content)
        print(f"🔗 Found {len(urls)} URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    def quick_similarity(url: str, product_name: str, brand: str = "") -> float:
        """Quick similarity calculation."""
        if not url or not product_name:
            return 0.0
        
        # Extract key words from URL filename
        filename = url.split('/')[-1].replace('.html', '').lower()
        url_words = set(re.findall(r'\w{3,}', filename))
        
        # Extract key words from product
        product_words = set(re.findall(r'\w{3,}', product_name.lower()))
        brand_words = set(re.findall(r'\w{3,}', brand.lower())) if brand else set()
        
        # Calculate overlap
        all_product_words = product_words.union(brand_words)
        common = url_words.intersection(all_product_words)
        
        if not url_words or not all_product_words:
            return 0.0
        
        # Simple Jaccard similarity with bonuses
        base_score = len(common) / len(url_words.union(all_product_words))
        
        # Bonus for brand match
        if brand_words and url_words.intersection(brand_words):
            base_score += 0.2
        
        # Bonus for important exact matches
        important_terms = ['stegulet', 'anvelopa', 'janta', 'casca', 'far', 'stop', 'husa']
        for term in important_terms:
            if term in product_name.lower() and term in filename:
                base_score += 0.15
                break
        
        return min(1.0, base_score)

    # Create URL index for faster lookup
    print("🔄 Creating product-URL matches...")
    
    matches = []
    for i, product in enumerate(products):
        if i % 1000 == 0:
            print(f"   Progress: {i}/{len(products)}")
        
        best_url = ""
        best_score = 0.0
        
        # Check only promising URLs (limit search for speed)
        for url in urls:
            score = quick_similarity(url, product['name'], product.get('brand', ''))
            if score > best_score and score > 0.15:  # Minimum threshold
                best_score = score
                best_url = url
        
        if best_url:
            matches.append((product, best_url, best_score))
    
    # Sort by similarity score (best matches first)
    matches.sort(key=lambda x: x[2], reverse=True)
    
    print(f"📊 Found {len(matches)} valid matches, assigning by best similarity...")
    
    # Reset URLs and assign based on best matches
    for product in products:
        product['url'] = ""
    
    used_urls = set()
    assigned = 0
    
    for product, url, score in matches:
        if url not in used_urls:
            product['url'] = url
            used_urls.add(url)
            assigned += 1
    
    print(f"✅ Assigned {assigned} unique URLs based on name similarity")
    
    # Save catalog
    data['last_updated'] = time.strftime("%Y-%m-%dT%H:%M:%S.000000")
    
    with open('../data/products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("💾 Catalog saved!")
    
    # Show examples of good matches
    with_urls = [p for p in products if p.get('url')]
    print(f"\n📋 Sample name-based matches ({len(with_urls)} total):")
    
    for product in with_urls[:5]:
        score = quick_similarity(product['url'], product['name'], product.get('brand', ''))
        print(f"   • {product['name'][:40]}")
        print(f"     Similarity: {score:.3f} | Price: {product['price']} RON")
        print(f"     URL: {product['url'][:50]}...")
        print()

if __name__ == "__main__":
    optimized_name_matching()
