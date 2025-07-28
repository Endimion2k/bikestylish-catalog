#!/usr/bin/env python3
"""
Correct Price Ranges - Manual correction with proper product matching
"""

import pandas as pd
import json

def correct_price_ranges():
    """Correct price ranges with better product matching"""
    
    print("🔧 Correcting price ranges with proper product matching...")
    
    # Load products
    try:
        df = pd.read_excel('../sxt26.xls')
        products = []
        for _, row in df.iterrows():
            product = {
                'name': str(row.get('nume_produs', '')).strip(),
                'description': str(row.get('descriere', '')).strip(),
                'price': float(row.get('pret_sugerat', 0)) if pd.notna(row.get('pret_sugerat')) else 0.0,
                'category': str(row.get('nume_categorie', '')).strip()
            }
            if product['price'] > 0:  # Only products with valid prices
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
        print(f"🗂️ Loaded {len(categories)} categories")
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Define strict matching rules for categories
    category_matching_rules = {
        'reflectorizante': ['reflector', 'reflect', 'stegulet', 'reflectorizant', 'catadioptru', 'reflectorizanta'],
        'lumini': ['lumina', 'led', 'far', 'light', 'lamp', 'lanterna'],
        'lumini-fata': ['lumina fata', 'far', 'front light', 'led fata'],
        'lumini-spate': ['lumina spate', 'stop', 'rear light', 'led spate'],
        'seturi-lumini': ['set lumini', 'lumini set', 'kit lumini'],
        'antifurturi': ['antifurt', 'lock', 'lacăt', 'blocare'],
        'pompe': ['pompa', 'pump', 'inflator', 'umflare'],
        'casti': ['casca', 'helmet', 'protectie cap'],
        'casti-ciclism-adulti': ['casca adult', 'helmet adult', 'casca ciclism'],
        'casti-bmx': ['casca bmx', 'helmet bmx'],
        'casti-full-face': ['casca full face', 'helmet full face'],
        'manusi': ['manusi', 'gloves', 'grip'],
        'anvelope': ['anvelopa', 'cauciuc', 'tire'],
        'anvelope-pe-sarma': ['anvelopa sarma', 'wire bead', 'anvelope sarma'],
        'anvelope-pliabile': ['anvelopa pliabila', 'folding tire', 'anvelope pliabile'],
        'camere': ['camera', 'tube', 'inner'],
        'camere-de-bicicleta': ['camera bicicleta', 'camera de aer'],
        'pedale': ['pedala', 'pedal'],
        'pedale-platforma': ['pedala platforma', 'platform pedal'],
        'pedale-click': ['pedala click', 'click pedal', 'clipless'],
        'pedale-duble': ['pedala dubla', 'dual pedal'],
        'scaune-pentru-copii': ['scaun copii', 'child seat', 'scaun bicicleta'],
        'cosuri-pentru-biciclete': ['cos', 'basket', 'cos bicicleta'],
        'roti-ajutatoare': ['roti ajutatoare', 'training wheels'],
        'accesorii': ['accesoriu', 'accessory'],
        'accesorii-bicicleta': ['accesoriu bicicleta', 'bike accessory'],
        'tricouri': ['tricou', 'jersey', 'shirt'],
        'tricouri-functionale': ['tricou functional', 'functional shirt'],
        'pantofi': ['pantof', 'shoe', 'boot'],
        'jachete': ['jacheta', 'jacket'],
        'aparatori-noroi': ['aparator', 'mudguard', 'fender'],
        'suport-bidon-si-bidon': ['bidon', 'bottle', 'suport apa'],
        'mansoane': ['manson', 'grip handle'],
        'ghidoline': ['ghidolina', 'bar tape'],
        'ghidoane': ['ghidon', 'handlebar'],
        'frane': ['frana', 'brake'],
        'frane-v-brake': ['frana v-brake', 'v-brake'],
        'placute-frana-disc': ['placuta frana', 'brake pad'],
        'saboti-frana': ['sabot frana', 'brake shoe'],
        'lanturi': ['lant', 'chain'],
        'șei': ['sa', 'saddle', 'scaun'],
        'huse-șa': ['husa sa', 'saddle cover']
    }
    
    # Calculate correct price ranges for each category
    updated_categories = []
    categories_corrected = 0
    
    for category in categories:
        updated_category = category.copy()
        cat_id = category['id']
        cat_name = category['name']
        
        # Get current price range
        real_data = category.get('real_data', {})
        old_range = real_data.get('price_range', {})
        old_min = old_range.get('min', 0)
        old_max = old_range.get('max', 0)
        
        # Find matching products for this category
        matching_prices = []
        
        # Use specific rules if available
        if cat_id in category_matching_rules:
            keywords = category_matching_rules[cat_id]
            
            for product in products:
                product_name = product['name'].lower()
                product_desc = product['description'].lower()
                product_cat = product['category'].lower()
                combined_text = f"{product_name} {product_desc} {product_cat}"
                
                # Check if any keyword matches
                for keyword in keywords:
                    if keyword in combined_text:
                        matching_prices.append(product['price'])
                        break
        else:
            # Use generic term matching
            cat_terms = cat_id.replace('-', ' ').split()
            
            for product in products:
                product_name = product['name'].lower()
                product_desc = product['description'].lower()
                product_cat = product['category'].lower()
                combined_text = f"{product_name} {product_desc} {product_cat}"
                
                # Check if any category term appears
                for term in cat_terms:
                    if len(term) > 2 and term in combined_text:
                        matching_prices.append(product['price'])
                        break
        
        # Calculate new price range
        if matching_prices:
            new_min = min(matching_prices)
            new_max = max(matching_prices)
            new_avg = sum(matching_prices) / len(matching_prices)
            
            # Update if different
            if abs(old_min - new_min) > 0.1 or abs(old_max - new_max) > 0.1:
                print(f"   ✅ {cat_name}: {old_min:.0f}-{old_max:.0f} → {new_min:.0f}-{new_max:.0f} RON ({len(matching_prices)} products)")
                
                # Update real_data
                if 'real_data' not in updated_category:
                    updated_category['real_data'] = {}
                
                updated_category['real_data']['price_range'] = {
                    'min': new_min,
                    'max': new_max,
                    'avg': new_avg
                }
                
                # Update schema markup if exists
                if ('content_structure' in updated_category and 
                    'schema_markup' in updated_category['content_structure'] and
                    'store_info' in updated_category['content_structure']['schema_markup']):
                    
                    updated_category['content_structure']['schema_markup']['store_info']['priceRange'] = f"{int(new_min)}-{int(new_max)} RON"
                
                categories_corrected += 1
        
        updated_categories.append(updated_category)
    
    # Save corrected data
    updated_data = data.copy()
    updated_data['categories'] = updated_categories
    
    try:
        with open('../data/categories_ai_enhanced.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Price ranges corrected successfully!")
        print(f"   Categories corrected: {categories_corrected}")
        
    except Exception as e:
        print(f"❌ Error saving corrected data: {e}")

if __name__ == "__main__":
    correct_price_ranges()
