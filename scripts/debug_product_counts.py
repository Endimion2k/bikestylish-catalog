#!/usr/bin/env python3
"""
Debug Product Count and Category Mapping Issues
"""

import pandas as pd
import json
from collections import defaultdict

def debug_product_mapping():
    """Debug why we have 40k+ product mappings when we only have 5k+ products"""
    
    print("🔍 Debugging product mapping issues...")
    
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
        
        print(f"📦 Total products in Excel: {len(products)}")
        products_with_price = [p for p in products if p['price'] > 0]
        print(f"💰 Products with valid prices: {len(products_with_price)}")
    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return
    
    # Load categories
    try:
        with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        categories = data['categories']
        
        # Count total mappings
        total_mappings = sum(cat.get('real_data', {}).get('product_count', 0) for cat in categories)
        print(f"🎯 Total product mappings in categories: {total_mappings:,}")
        
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Check specific categories with suspicious numbers
    print(f"\n🔍 Checking suspicious categories:")
    
    suspicious_categories = ['lumini', 'lumini-fata', 'lumini-spate', 'cosuri-pentru-biciclete', 'scaune-pentru-copii']
    
    for cat_id in suspicious_categories:
        cat = next((c for c in categories if c['id'] == cat_id), None)
        if cat:
            product_count = cat.get('real_data', {}).get('product_count', 0)
            price_range = cat.get('real_data', {}).get('price_range', {})
            min_price = price_range.get('min', 0)
            max_price = price_range.get('max', 0)
            
            print(f"\n📊 {cat['name']} ({cat_id}):")
            print(f"   Product count: {product_count:,}")
            print(f"   Price range: {min_price:.0f} - {max_price:.0f} RON")
            
            # Find actual products that might match this category
            matching_products = []
            cat_terms = cat_id.replace('-', ' ').split()
            
            for product in products_with_price[:500]:  # Check first 500 products
                product_name = product['name'].lower()
                product_cat = product['category'].lower()
                
                # Check if product really matches this category
                is_match = False
                for term in cat_terms:
                    if len(term) > 2 and (term in product_name or term in product_cat):
                        is_match = True
                        break
                
                if is_match:
                    matching_products.append(product)
            
            print(f"   Actual matches in sample: {len(matching_products)}")
            if matching_products:
                actual_prices = [p['price'] for p in matching_products]
                actual_min = min(actual_prices)
                actual_max = max(actual_prices)
                print(f"   Actual price range: {actual_min:.0f} - {actual_max:.0f} RON")
                
                print(f"   Sample products:")
                for i, product in enumerate(matching_products[:5]):
                    print(f"      {i+1}. {product['name'][:60]}... - {product['price']:.0f} RON")
            
            # Check if the count seems inflated
            if product_count > len(matching_products) * 10:
                print(f"   ⚠️  COUNT SEEMS INFLATED! {product_count:,} vs ~{len(matching_products)*10}")

def check_lumini_specifically():
    """Check lumini category specifically"""
    
    print(f"\n🔍 Checking 'lumini' category specifically...")
    
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
        
        print(f"📦 Products with valid prices: {len(products)}")
    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return
    
    # Find products that really contain "lumini", "led", "light", etc.
    lumini_keywords = ['lumina', 'led', 'far', 'light', 'lamp', 'lanterna', 'flash', 'stop']
    real_lumini_products = []
    
    for product in products:
        product_name = product['name'].lower()
        product_cat = product['category'].lower()
        combined = f"{product_name} {product_cat}"
        
        for keyword in lumini_keywords:
            if keyword in combined:
                real_lumini_products.append(product)
                break
    
    print(f"💡 Real lumini products found: {len(real_lumini_products)}")
    
    if real_lumini_products:
        prices = [p['price'] for p in real_lumini_products]
        real_min = min(prices)
        real_max = max(prices)
        real_avg = sum(prices) / len(prices)
        
        print(f"   Real price range: {real_min:.0f} - {real_max:.0f} RON")
        print(f"   Real average price: {real_avg:.0f} RON")
        
        print(f"\n   Sample real lumini products:")
        for i, product in enumerate(real_lumini_products[:10]):
            print(f"      {i+1}. {product['name'][:60]}... - {product['price']:.0f} RON")
    
    # Check what the minimum realistic price should be
    cheap_lumini = [p for p in real_lumini_products if p['price'] < 10]
    if cheap_lumini:
        print(f"\n   Products under 10 RON:")
        for product in cheap_lumini[:5]:
            print(f"      - {product['name'][:60]}... - {product['price']:.0f} RON")
    else:
        print(f"\n   ✅ No products under 10 RON found - minimum should be around 10-15 RON")

if __name__ == "__main__":
    debug_product_mapping()
    check_lumini_specifically()
