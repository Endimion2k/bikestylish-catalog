#!/usr/bin/env python3
"""
Validate Real Data Integration Results
"""

import json

def validate_results():
    """Validate the final results"""
    
    print("🔍 Validating real data integration results...")
    
    try:
        with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = data['categories']
        print(f"📊 Total Categories: {len(categories)}")
        
        # Count categories with products
        with_products = sum(1 for c in categories if c.get('real_data', {}).get('product_count', 0) > 0)
        print(f"📦 Categories with Products: {with_products}/{len(categories)}")
        
        # Total product mappings
        total_products = sum(c.get('real_data', {}).get('product_count', 0) for c in categories)
        print(f"🎯 Total Product Mappings: {total_products:,}")
        
        # Top categories by product count
        sorted_cats = sorted(categories, key=lambda x: x.get('real_data', {}).get('product_count', 0), reverse=True)[:10]
        
        print(f"\n🏆 Top 10 Categories by Product Count:")
        for i, cat in enumerate(sorted_cats, 1):
            product_count = cat.get('real_data', {}).get('product_count', 0)
            price_range = cat.get('real_data', {}).get('price_range', {})
            min_price = price_range.get('min', 0)
            max_price = price_range.get('max', 0)
            brands = len(cat.get('real_data', {}).get('brands', []))
            faqs = len(cat.get('content_structure', {}).get('faq_data', []))
            
            print(f"   {i:2d}. {cat['name']}: {product_count:,} products")
            print(f"       Price Range: {min_price:.0f}-{max_price:.0f} RON")
            print(f"       Brands: {brands}, FAQs: {faqs}")
        
        # Categories without products
        without_products = [c for c in categories if c.get('real_data', {}).get('product_count', 0) == 0]
        if without_products:
            print(f"\n⚠️  Categories without products: {len(without_products)}")
            for cat in without_products:
                print(f"   - {cat['name']} ({cat['id']})")
        
        print(f"\n✅ Real Data Integration Complete!")
        print(f"   Success Rate: {with_products/len(categories)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Error validating results: {e}")

if __name__ == "__main__":
    validate_results()
