#!/usr/bin/env python3
"""
Fix Price Ranges - Recalculate correctly from real products in each category
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

def find_product_categories(product: Dict, category_lookup: Dict) -> List[str]:
    """Find which categories a product belongs to"""
    
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
    
    # If no direct match, try to infer from product type
    if not matched_categories:
        matched_categories = infer_category_from_product(product, category_lookup)
    
    return matched_categories

def infer_category_from_product(product: Dict, category_lookup: Dict) -> List[str]:
    """Infer category from product characteristics"""
    
    product_name = product.get('name', '').lower()
    product_desc = product.get('description', '').lower()
    combined_text = f"{product_name} {product_desc}"
    
    matched_categories = []
    
    # Enhanced inference rules
    inference_rules = {
        'lumini': ['lumina', 'led', 'far', 'stop', 'light', 'lamp', 'lanterna', 'flash'],
        'reflectorizante': ['reflector', 'reflect', 'visibility', 'reflectorizant', 'stegulet', 'reflectors'],
        'antifurt': ['antifurt', 'lock', 'security', 'lacăt', 'blocare'],
        'pompe': ['pompă', 'pump', 'inflate', 'umflare', 'presiune'],
        'casti': ['casca', 'helmet', 'cască', 'cap', 'protecție'],
        'manusi': ['mănuși', 'gloves', 'mâini', 'grip'],
        'tricouri': ['tricou', 'jersey', 'shirt', 'îmbrăcăminte'],
        'pantaloni': ['pantaloni', 'shorts', 'bibshort', 'colant'],
        'anvelope': ['anvelopă', 'tire', 'cauciuc', 'roată'],
        'camere': ['cameră', 'tube', 'inner', 'valvă'],
        'pedale': ['pedală', 'pedal', 'click', 'platformă'],
        'șei': ['șa', 'saddle', 'seat', 'scaun'],
        'ghidoane': ['ghidon', 'handlebar', 'bar', 'directionare'],
        'frane': ['frână', 'brake', 'disc', 'plăcuță', 'saboti'],
        'schimbatoare': ['schimbător', 'derailleur', 'viteze', 'transmisie'],
        'lanturi': ['lanț', 'chain', 'transmisie', 'angrenaj'],
        'roti': ['roată', 'wheel', 'butuc', 'jantă'],
        'scule': ['cheie', 'tool', 'reparare', 'demontare', 'service'],
        'cosuri': ['coș', 'basket', 'transport', 'încărcătură'],
        'aparatori': ['apărător', 'mudguard', 'noroi', 'protecție'],
        'suporturi': ['suport', 'support', 'holder', 'mount']
    }
    
    # Find matching categories based on inference
    for pattern, keywords in inference_rules.items():
        for keyword in keywords:
            if keyword in combined_text:
                # Find categories that match this pattern
                for cat_id in category_lookup:
                    if pattern in cat_id or any(pattern in term for term in cat_id.split('-')):
                        matched_categories.append(cat_id)
                break
    
    # Special handling for specific product types
    if 'copii' in combined_text or 'child' in combined_text:
        for cat_id in category_lookup:
            if 'copii' in cat_id:
                matched_categories.append(cat_id)
    
    if 'e-bike' in combined_text or 'electric' in combined_text:
        for cat_id in category_lookup:
            if 'e-bike' in cat_id:
                matched_categories.append(cat_id)
    
    # Remove duplicates
    return list(dict.fromkeys(matched_categories))

def fix_price_ranges():
    """Fix price ranges by recalculating from real products"""
    
    print("🔧 Fixing price ranges...")
    
    # Load products
    products = load_product_data()
    if not products:
        return
    
    # Load categories
    try:
        with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        categories = data['categories']
        category_lookup = {cat['id']: cat for cat in categories}
        print(f"🗂️ Loaded {len(categories)} categories")
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Recalculate price ranges for each category
    category_prices = defaultdict(list)
    
    print("🔍 Re-matching products to categories for price calculation...")
    for i, product in enumerate(products):
        if i % 1000 == 0:
            print(f"   Processing product {i+1}/{len(products)}...")
        
        price = product.get('price', 0)
        if price <= 0:
            continue
            
        matched_categories = find_product_categories(product, category_lookup)
        
        for cat_id in matched_categories:
            if cat_id in category_lookup:
                category_prices[cat_id].append(price)
    
    # Update categories with correct price ranges
    updated_categories = []
    categories_fixed = 0
    
    for category in categories:
        updated_category = category.copy()
        cat_id = category['id']
        
        if cat_id in category_prices and category_prices[cat_id]:
            prices = category_prices[cat_id]
            real_min = min(prices)
            real_max = max(prices)
            real_avg = sum(prices) / len(prices)
            
            # Update real_data with correct price range
            if 'real_data' in updated_category:
                old_range = updated_category['real_data'].get('price_range', {})
                old_min = old_range.get('min', 0)
                old_max = old_range.get('max', 0)
                
                updated_category['real_data']['price_range'] = {
                    'min': real_min,
                    'max': real_max,
                    'avg': real_avg
                }
                
                if old_min != real_min or old_max != real_max:
                    print(f"   ✅ Fixed {category['name']}: {old_min:.0f}-{old_max:.0f} → {real_min:.0f}-{real_max:.0f} RON")
                    categories_fixed += 1
                    
                # Also update schema markup if it exists
                if 'content_structure' in updated_category and 'schema_markup' in updated_category['content_structure']:
                    schema = updated_category['content_structure']['schema_markup']
                    if 'store_info' in schema:
                        schema['store_info']['priceRange'] = f"{int(real_min)}-{int(real_max)} RON"
        
        updated_categories.append(updated_category)
    
    # Save updated data
    updated_data = data.copy()
    updated_data['categories'] = updated_categories
    
    try:
        with open('../data/categories_ai_enhanced.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Price ranges fixed successfully!")
        print(f"   Categories updated: {categories_fixed}")
        print(f"   Total categories with real prices: {len(category_prices)}")
        
    except Exception as e:
        print(f"❌ Error saving fixed data: {e}")

if __name__ == "__main__":
    fix_price_ranges()
