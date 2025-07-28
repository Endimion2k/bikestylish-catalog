#!/usr/bin/env python3
"""
Debug product-category matching
"""

import json

def debug_matching():
    """Debug why products don't match categories"""
    
    print("🔍 Debugging product-category matching...")
    
    # Load products
    with open('../data/products_ai_enhanced.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    products = catalog.get('products', [])
    print(f"📦 Found {len(products)} products")
    
    # Load categories
    with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
        categories_data = json.load(f)
    
    categories = categories_data.get('categories', [])
    print(f"🗂️ Found {len(categories)} categories")
    
    # Analyze first few products
    print(f"\n📋 Sample Products:")
    for i, product in enumerate(products[:10]):
        print(f"  {i+1}. {product.get('name', 'N/A')}")
        print(f"     Brand: {product.get('brand', 'N/A')}")
        print(f"     Category: {product.get('category', 'N/A')}")
        print(f"     Price: {product.get('price', 'N/A')}")
        print(f"     Description: {product.get('description', 'N/A')[:50]}...")
        print()
    
    # Analyze categories
    print(f"📋 Sample Categories:")
    for i, category in enumerate(categories[:10]):
        print(f"  {i+1}. {category.get('name', 'N/A')} ({category.get('id', 'N/A')})")
    
    # Test specific product matching
    test_product = products[0]  # First product
    print(f"\n🔍 Testing product matching for: {test_product.get('name', 'N/A')}")
    
    product_name = test_product.get('name', '').lower()
    product_desc = test_product.get('description', '').lower()
    product_cat = test_product.get('category', '').lower()
    
    print(f"   Name (lower): {product_name}")
    print(f"   Description (lower): {product_desc}")
    print(f"   Category (lower): {product_cat}")
    
    # Test category matching
    category_lookup = {cat['id']: cat for cat in categories}
    
    matched_categories = []
    for cat_id, cat_info in category_lookup.items():
        cat_name = cat_info['name'].lower()
        cat_terms = cat_id.replace('-', ' ').split()
        
        print(f"\n   Testing category: {cat_id} ({cat_name})")
        print(f"   Category terms: {cat_terms}")
        
        # Check if any category terms appear in product data
        for term in cat_terms:
            if len(term) > 2:
                if (term in product_name or 
                    term in product_desc or 
                    term in product_cat):
                    print(f"   ✅ MATCH found with term: {term}")
                    matched_categories.append(cat_id)
                    break
                else:
                    print(f"   ❌ No match with term: {term}")
    
    print(f"\n📊 Matched categories: {matched_categories}")
    
    # Test inference rules
    print(f"\n🧠 Testing inference rules:")
    combined_text = f"{product_name} {product_desc}"
    
    inference_rules = {
        'lumini': ['lumina', 'led', 'far', 'stop', 'light', 'lamp', 'lanterna'],
        'reflectorizante': ['reflector', 'reflect', 'visibility', 'reflectorizant', 'stegulet'],
        'stegulet': ['stegulet', 'flag', 'banner']
    }
    
    for pattern, keywords in inference_rules.items():
        print(f"   Pattern {pattern}: {keywords}")
        for keyword in keywords:
            if keyword in combined_text:
                print(f"   ✅ INFERENCE MATCH: {keyword} in text")
                break
        else:
            print(f"   ❌ No inference match for {pattern}")

if __name__ == "__main__":
    debug_matching()
