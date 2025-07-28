#!/usr/bin/env python3
"""
Debug Specific Category Price Range
"""

import pandas as pd
import json

def debug_specific_category():
    """Debug a specific category in detail"""
    
    print("🔍 Debugging specific category: Reflectorizante")
    
    # Load products
    try:
        df = pd.read_excel('../sxt26.xls')
        products = []
        for _, row in df.iterrows():
            product = {
                'name': str(row.get('nume_produs', '')).strip(),
                'price': float(row.get('pret_sugerat', 0)) if pd.notna(row.get('pret_sugerat')) else 0.0,
                'category': str(row.get('nume_categorie', '')).strip()
            }
            if product['price'] > 0:
                products.append(product)
        
        print(f"📦 Loaded {len(products)} products with valid prices")
    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return
    
    # Load categories
    try:
        with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        categories = data['categories']
        
        # Find Reflectorizante category
        reflectorizante_cat = None
        for cat in categories:
            if cat['id'] == 'reflectorizante':
                reflectorizante_cat = cat
                break
        
        if not reflectorizante_cat:
            print("❌ Category 'reflectorizante' not found")
            return
            
        print(f"🗂️ Found category: {reflectorizante_cat['name']}")
        
        # Check stored price range
        real_data = reflectorizante_cat.get('real_data', {})
        stored_range = real_data.get('price_range', {})
        print(f"📊 Stored price range: {stored_range}")
        
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Find products that should match 'reflectorizante'
    matching_products = []
    reflector_terms = ['reflector', 'reflect', 'stegulet', 'reflectorizant', 'reflectorizante']
    
    for product in products:
        product_name = product['name'].lower()
        product_cat = product['category'].lower()
        
        # Check if product matches reflectorizante
        is_match = False
        
        # Direct term matching
        for term in reflector_terms:
            if term in product_name or term in product_cat:
                is_match = True
                break
        
        # Category ID term matching
        if 'reflect' in product_name or 'reflect' in product_cat:
            is_match = True
            
        if is_match:
            matching_products.append(product)
    
    if matching_products:
        prices = [p['price'] for p in matching_products]
        actual_min = min(prices)
        actual_max = max(prices)
        actual_avg = sum(prices) / len(prices)
        
        print(f"\n📈 Found {len(matching_products)} matching products:")
        print(f"   Actual price range: {actual_min:.0f} - {actual_max:.0f} RON")
        print(f"   Average price: {actual_avg:.0f} RON")
        
        # Show sample products
        print(f"\n📝 Sample matching products:")
        for i, product in enumerate(matching_products[:10]):
            print(f"   {i+1}. {product['name'][:50]}... - {product['price']:.0f} RON")
            
        # Compare with stored
        stored_min = stored_range.get('min', 0)
        stored_max = stored_range.get('max', 0)
        
        if stored_min != actual_min or stored_max != actual_max:
            print(f"\n⚠️  MISMATCH CONFIRMED!")
            print(f"   Stored: {stored_min:.0f} - {stored_max:.0f} RON")
            print(f"   Actual: {actual_min:.0f} - {actual_max:.0f} RON")
        else:
            print(f"\n✅ Price ranges match!")
    else:
        print(f"❌ No matching products found for reflectorizante category")

if __name__ == "__main__":
    debug_specific_category()
