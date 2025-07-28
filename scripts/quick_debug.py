#!/usr/bin/env python3
"""
Quick Debug - Check Category Product Data Analysis
"""

import pandas as pd
import json
from collections import defaultdict
from typing import Dict, List

def load_product_data():
    """Load product data from Excel file"""
    
    try:
        df = pd.read_excel('../sxt26.xls')
        products = []
        for _, row in df.iterrows():
            product = {
                'name': str(row.get('nume_produs', '')).strip(),
                'description': str(row.get('descriere', '')).strip(),
                'price': float(row.get('pret_sugerat', 0)) if pd.notna(row.get('pret_sugerat')) else 0.0,
                'brand': str(row.get('producator', '')).strip(),
                'category': str(row.get('nume_categorie', '')).strip()
            }
            products.append(product)
        
        print(f"📦 Loaded {len(products)} products from Excel file")
        return products
        
    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return []

def debug_analyze_products_by_category():
    """Debug the analyze_products_by_category function"""
    
    print("🔍 Debug - Analyzing products by category...")
    
    # Load products
    products = load_product_data()
    if not products:
        return
    
    # Load categories
    try:
        with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        categories = categories_data.get('categories', [])
        category_lookup = {cat['id']: cat for cat in categories}
        print(f"🗂️ Loaded {len(categories)} categories")
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Initialize category data tracking
    category_data = defaultdict(lambda: {
        'products': [],
        'product_count': 0,
        'price_range': {'min': float('inf'), 'max': 0, 'avg': 0},
        'brands': set(),
        'common_terms': []
    })
    
    # Test first 10 products
    test_products = products[:10]
    total_matches = 0
    
    for i, product in enumerate(test_products):
        print(f"\n🧪 Testing product {i+1}: {product['name'][:50]}...")
        
        # Test the find_product_categories function directly
        matched_categories = find_product_categories_inline(product, category_lookup)
        
        if matched_categories:
            print(f"   ✅ Found {len(matched_categories)} matches: {matched_categories[:3]}")
            total_matches += len(matched_categories)
            
            # Add to category data
            price = product.get('price', 0)
            brand = product.get('brand', '')
            
            for cat_id in matched_categories:
                if cat_id in category_lookup:  # Check if cat_id exists in lookup
                    category_data[cat_id]['products'].append(product)
                    category_data[cat_id]['product_count'] += 1
                    print(f"      → Added to {cat_id} (now {category_data[cat_id]['product_count']} products)")
        else:
            print(f"   ❌ No matches found")
    
    print(f"\n📊 Debug Results:")
    print(f"   Total matches: {total_matches}")
    print(f"   Categories with products: {len([cat for cat in category_data.values() if cat['product_count'] > 0])}")
    
    # Show categories with products
    for cat_id, data in category_data.items():
        if data['product_count'] > 0:
            print(f"   📦 {cat_id}: {data['product_count']} products")

def find_product_categories_inline(product: Dict, category_lookup: Dict) -> List[str]:
    """Inline copy of find_product_categories function"""
    
    product_name = product.get('name', '').lower()
    product_desc = product.get('description', '').lower()
    product_cat = product.get('category', '').lower()
    
    matched_categories = []
    
    # Try direct category matching
    for cat_id, cat_info in category_lookup.items():
        cat_name = cat_info['name'].lower()
        cat_terms = cat_id.replace('-', ' ').split()
        
        # Check if any category terms appear in product data
        found_match = False
        for term in cat_terms:
            if len(term) > 2:  # Ignore very short terms
                if (term in product_name or 
                    term in product_desc or 
                    term in product_cat):
                    matched_categories.append(cat_id)
                    found_match = True
                    break
        
        if found_match:
            continue
            
        # Also check if category name appears in product
        for term in cat_name.split():
            if len(term) > 2 and term in product_name:
                matched_categories.append(cat_id)
                break
    
    # Remove duplicates while preserving order
    matched_categories = list(dict.fromkeys(matched_categories))
    
    return matched_categories

if __name__ == "__main__":
    debug_analyze_products_by_category()
