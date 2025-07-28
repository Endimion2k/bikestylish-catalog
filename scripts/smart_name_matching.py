import json
import re
from collections import defaultdict
from typing import Dict, Set, Tuple
import time

def smart_name_based_url_matching():
    """Smart URL matching based on product name similarity, not price."""
    print("🧠 Smart name-based URL matching...")
    
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
        print(f"🔗 Found {len(urls)} URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    def calculate_name_similarity(url: str, product: Dict) -> float:
        """Calculate similarity score based on product name and URL."""
        if not url or not product.get('name'):
            return 0.0
        
        # Extract filename from URL
        filename = url.split('/')[-1].replace('.html', '').lower()
        filename_clean = re.sub(r'[^\w\s-]', ' ', filename)
        filename_words = set(w for w in filename_clean.split() if len(w) > 2)
        
        # Clean product name
        product_name = product['name'].lower()
        product_clean = re.sub(r'[^\w\s-]', ' ', product_name)
        product_words = set(w for w in product_clean.split() if len(w) > 2)
        
        # Brand matching
        brand = product.get('brand', '').lower()
        brand_words = set(w for w in brand.split() if len(w) > 2) if brand else set()
        
        if not filename_words or not product_words:
            return 0.0
        
        # Calculate word overlap
        common_words = filename_words.intersection(product_words)
        total_unique_words = len(filename_words.union(product_words))
        
        if total_unique_words == 0:
            return 0.0
        
        # Base similarity score (Jaccard similarity)
        base_score = len(common_words) / total_unique_words
        
        # Bonus for brand match in URL
        brand_bonus = 0.0
        if brand_words and filename_words.intersection(brand_words):
            brand_bonus = 0.2
        
        # Bonus for exact word matches (especially important words)
        important_words = {'stegulet', 'anvelopa', 'janta', 'casca', 'manusi', 'husa', 'far', 'stop'}
        exact_match_bonus = 0.0
        for word in important_words:
            if word in product_clean and word in filename:
                exact_match_bonus += 0.15
        
        # Penalty for generic mismatches
        penalty = 0.0
        generic_terms = {'accesorii', 'piese', 'bicicleta', 'bike', 'cycling'}
        if len(common_words) <= 1 and filename_words.intersection(generic_terms):
            penalty = 0.3
        
        final_score = base_score + brand_bonus + exact_match_bonus - penalty
        return max(0.0, min(1.0, final_score))

    # Create list of (product, best_url, score) tuples
    product_url_matches = []
    
    print("🔄 Calculating similarity scores for all product-URL combinations...")
    
    for i, product in enumerate(products):
        if i % 1000 == 0:
            print(f"   Progress: {i}/{len(products)}")
        
        best_url = ""
        best_score = 0.0
        
        for url in urls:
            score = calculate_name_similarity(url, product)
            if score > best_score:
                best_score = score
                best_url = url
        
        if best_score > 0.1:  # Minimum threshold
            product_url_matches.append((product, best_url, best_score))
    
    print(f"📊 Found {len(product_url_matches)} potential matches")
    
    # Sort by similarity score (highest first) to prioritize best matches
    product_url_matches.sort(key=lambda x: x[2], reverse=True)
    
    # Assign URLs ensuring no duplicates
    used_urls = set()
    matched_count = 0
    
    # Reset all URLs first
    for product in products:
        product['url'] = ""
    
    print("🔄 Assigning URLs based on best name matches...")
    
    for product, url, score in product_url_matches:
        if url not in used_urls:
            product['url'] = url
            used_urls.add(url)
            matched_count += 1
    
    print(f"✅ Matched {matched_count}/{len(products)} products with unique URLs")
    
    # Update catalog metadata
    data['last_updated'] = time.strftime("%Y-%m-%dT%H:%M:%S.000000")
    
    # Save updated catalog
    with open('../data/products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("💾 Catalog saved!")
    
    # Show sample results with scores
    with_urls = [p for p in products if p.get('url')]
    print(f"\n📋 Sample results ({len(with_urls)} total with URLs):")
    
    # Show some specific examples
    sample_products = with_urls[:5]
    for product in sample_products:
        # Calculate score for display
        display_score = calculate_name_similarity(product['url'], product)
        print(f"   • {product['name'][:45]}")
        print(f"     Score: {display_score:.3f} | Price: {product['price']} RON")
        print(f"     URL: {product['url'][:55]}...")
        print()

if __name__ == "__main__":
    smart_name_based_url_matching()
