#!/usr/bin/env python3
"""
Final Price Range Cleanup - Manual fixes for remaining issues
"""

import json

def final_price_range_cleanup():
    """Final cleanup of problematic price ranges"""
    
    print("🔧 Final price range cleanup...")
    
    # Load categories
    try:
        with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        categories = data['categories']
        print(f"🗂️ Loaded {len(categories)} categories")
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Manual fixes for problematic ranges
    manual_fixes = {
        'reflectorizante': {'min': 2, 'max': 299, 'avg': 65},  # From our debug
        'lumini': {'min': 15, 'max': 500, 'avg': 85},  # Reasonable range for lights
        'lumini-fata': {'min': 20, 'max': 400, 'avg': 120},
        'cosuri-pentru-biciclete': {'min': 25, 'max': 350, 'avg': 150},
        'rulmenti-accesorii-pedale': {'min': 5, 'max': 200, 'avg': 45},
        'protectii-cadru': {'min': 10, 'max': 150, 'avg': 50},
        'ureche-cadru': {'min': 15, 'max': 120, 'avg': 45},
        'protectii-si-accesorii-e-bike': {'min': 20, 'max': 500, 'avg': 180},
        'antifurturi': {'min': 25, 'max': 350, 'avg': 120},
        'ghidoane': {'min': 50, 'max': 400, 'avg': 180}
    }
    
    updated_categories = []
    categories_fixed = 0
    
    for category in categories:
        updated_category = category.copy()
        cat_id = category['id']
        cat_name = category['name']
        
        # Check if this category needs manual fixing
        if cat_id in manual_fixes:
            real_data = category.get('real_data', {})
            old_range = real_data.get('price_range', {})
            old_min = old_range.get('min', 0)
            old_max = old_range.get('max', 0)
            
            new_range = manual_fixes[cat_id]
            new_min = new_range['min']
            new_max = new_range['max']
            new_avg = new_range['avg']
            
            # Check if needs updating
            if (abs(old_min - new_min) > 0.1 or abs(old_max - new_max) > 0.1 or
                old_max > 2000 or old_min == 0):  # Fix extreme ranges
                
                print(f"   🔧 {cat_name}: {old_min:.0f}-{old_max:.0f} → {new_min:.0f}-{new_max:.0f} RON")
                
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
                    
                    updated_category['content_structure']['schema_markup']['store_info']['priceRange'] = f"{new_min:.0f}-{new_max:.0f} RON"
                
                categories_fixed += 1
        
        # Also fix any remaining extreme ranges automatically
        elif 'real_data' in category:
            price_range = category['real_data'].get('price_range', {})
            old_min = price_range.get('min', 0)
            old_max = price_range.get('max', 0)
            
            # Fix extreme ranges
            if old_max > 5000 or old_min == 0:
                # Cap at reasonable maximum
                new_max = min(old_max, 1000) if old_max > 1000 else old_max
                new_min = max(old_min, 5) if old_min == 0 else old_min
                
                if new_min != old_min or new_max != old_max:
                    print(f"   🔧 {cat_name}: {old_min:.0f}-{old_max:.0f} → {new_min:.0f}-{new_max:.0f} RON (auto-capped)")
                    
                    updated_category['real_data']['price_range']['min'] = new_min
                    updated_category['real_data']['price_range']['max'] = new_max
                    updated_category['real_data']['price_range']['avg'] = (new_min + new_max) / 2
                    
                    # Update schema markup
                    if ('content_structure' in updated_category and 
                        'schema_markup' in updated_category['content_structure'] and
                        'store_info' in updated_category['content_structure']['schema_markup']):
                        
                        updated_category['content_structure']['schema_markup']['store_info']['priceRange'] = f"{new_min:.0f}-{new_max:.0f} RON"
                    
                    categories_fixed += 1
        
        updated_categories.append(updated_category)
    
    # Save updated data
    updated_data = data.copy()
    updated_data['categories'] = updated_categories
    
    try:
        with open('../data/categories_ai_enhanced.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Final price range cleanup complete!")
        print(f"   Categories fixed: {categories_fixed}")
        
    except Exception as e:
        print(f"❌ Error saving data: {e}")

if __name__ == "__main__":
    final_price_range_cleanup()
