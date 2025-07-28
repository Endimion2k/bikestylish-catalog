#!/usr/bin/env python3
"""
Debug Price Range Calculation
"""

import pandas as pd
import json

def debug_price_ranges():
    """Debug price range calculation for categories"""
    
    print("🔍 Debugging price range calculations...")
    
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
            products.append(product)
        
        print(f"📦 Loaded {len(products)} products")
    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return
    
    # Load enhanced categories 
    try:
        with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        categories = data['categories']
        print(f"🗂️ Loaded {len(categories)} categories")
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Check top categories with most products
    sorted_cats = sorted(categories, key=lambda x: x.get('real_data', {}).get('product_count', 0), reverse=True)[:5]
    
    for cat in sorted_cats:
        cat_id = cat['id']
        cat_name = cat['name']
        real_data = cat.get('real_data', {})
        
        if real_data.get('product_count', 0) > 0:
            # Get stored price range
            stored_range = real_data.get('price_range', {})
            stored_min = stored_range.get('min', 0)
            stored_max = stored_range.get('max', 0)
            
            print(f"\n📊 Category: {cat_name} ({cat_id})")
            print(f"   Stored range: {stored_min:.0f} - {stored_max:.0f} RON")
            print(f"   Product count: {real_data.get('product_count', 0)}")
            
            # Calculate actual price range from products that should match this category
            # Let's check some sample products to see if range makes sense
            matching_products = []
            cat_terms = cat_id.replace('-', ' ').split()
            
            # Simple matching check
            for product in products[:1000]:  # Check first 1000 products
                product_name = product['name'].lower()
                product_cat = product['category'].lower()
                
                # Check if product might belong to this category
                for term in cat_terms:
                    if len(term) > 2 and (term in product_name or term in product_cat):
                        if product['price'] > 0:
                            matching_products.append(product['price'])
                        break
            
            if matching_products:
                actual_min = min(matching_products)
                actual_max = max(matching_products)
                print(f"   Sample actual range: {actual_min:.0f} - {actual_max:.0f} RON (from {len(matching_products)} samples)")
                
                if stored_min != actual_min or stored_max != actual_max:
                    print(f"   ⚠️  MISMATCH! Stored range differs from sample calculation")
            else:
                print(f"   ❌ No matching products found in sample")

if __name__ == "__main__":
    debug_price_ranges()
