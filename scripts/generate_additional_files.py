#!/usr/bin/env python3
"""
Generate separate category and brand files from the main catalog
"""

import json
from datetime import datetime

def create_categories_file():
    """Create a separate categories.json file."""
    
    # Load main catalog
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Create detailed categories structure
    categories_data = {
        "last_updated": datetime.now().isoformat(),
        "total_categories": len(catalog['categories']),
        "categories": []
    }
    
    # Enhanced category information
    for category in catalog['categories']:
        cat_id = category['id']
        
        # Get products in this category
        category_products = [p for p in catalog['products'] if p['category'] == cat_id]
        
        # Calculate subcategories and stats
        subcategories = []
        if cat_id == 'accesorii':
            subcategories = [
                {"id": "reflectorizante", "name": "Reflectorizante", "count": len([p for p in category_products if 'reflector' in p['name'].lower() or 'stegulet' in p['name'].lower()])},
                {"id": "antifurturi", "name": "Antifurturi", "count": len([p for p in category_products if 'antifurt' in p['name'].lower()])},
                {"id": "copii", "name": "Articole pentru Copii", "count": len([p for p in category_products if 'copii' in p['name'].lower() or 'scaun' in p['name'].lower()])},
                {"id": "transport", "name": "Transport și Depozitare", "count": len([p for p in category_products if 'suport' in p['name'].lower() or 'stand' in p['name'].lower()])}
            ]
        elif cat_id == 'biciclete':
            subcategories = [
                {"id": "trotinete", "name": "Trotinete", "count": len([p for p in category_products if 'trotineta' in p['name'].lower()])},
                {"id": "copii", "name": "Biciclete pentru Copii", "count": len([p for p in category_products if 'copii' in p['name'].lower()])}
            ]
        elif cat_id == 'piese-schimb':
            subcategories = [
                {"id": "anvelope", "name": "Anvelope", "count": len([p for p in category_products if 'anvelopa' in p['name'].lower()])},
                {"id": "camere", "name": "Camere", "count": len([p for p in category_products if 'camera' in p['name'].lower()])}
            ]
        
        # Price range
        prices = [p['price'] for p in category_products if p['price'] > 0]
        price_range = {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "avg": round(sum(prices)/len(prices), 2) if prices else 0,
            "currency": "RON"
        }
        
        categories_data['categories'].append({
            "id": cat_id,
            "name": category['name'],
            "count": category['count'],
            "subcategories": subcategories,
            "price_range": price_range,
            "top_brands": list(set([p['brand'] for p in category_products]))[:5]
        })
    
    # Save categories file
    with open('../data/categories.json', 'w', encoding='utf-8') as f:
        json.dump(categories_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created categories.json with {len(categories_data['categories'])} categories")

def create_brands_file():
    """Create a separate brands.json file."""
    
    # Load main catalog
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Create detailed brands structure
    brands_data = {
        "last_updated": datetime.now().isoformat(),
        "total_brands": len(catalog['brands']),
        "brands": []
    }
    
    # Enhanced brand information
    for brand in catalog['brands']:
        brand_name = brand['name']
        
        # Get products from this brand
        brand_products = [p for p in catalog['products'] if p['brand'] == brand_name]
        
        # Calculate categories this brand covers
        categories = list(set([p['category'] for p in brand_products]))
        
        # Price range
        prices = [p['price'] for p in brand_products if p['price'] > 0]
        price_range = {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "avg": round(sum(prices)/len(prices), 2) if prices else 0,
            "currency": "RON"
        }
        
        # Determine origin/country based on brand name
        origin = "Unknown"
        if brand_name in ["M-WAVE", "CONTINENTAL"]:
            origin = "Germany"
        elif brand_name == "SXT":
            origin = "Romania"
        elif brand_name in ["SPECIALIZED", "TREK", "CANNONDALE", "SRAM"]:
            origin = "USA"
        elif brand_name in ["GIANT", "MERIDA"]:
            origin = "Taiwan"
        elif brand_name == "SHIMANO":
            origin = "Japan"
        elif brand_name == "SCOTT":
            origin = "Switzerland"
        elif brand_name in ["KENDA"]:
            origin = "Taiwan"
        elif brand_name == "BELELLI":
            origin = "Italy"
        
        brands_data['brands'].append({
            "name": brand_name,
            "product_count": brand['product_count'],
            "categories": categories,
            "price_range": price_range,
            "origin": origin,
            "avg_rating": round(4.0 + (hash(brand_name) % 10) * 0.1, 1),  # Simulated rating
            "description": f"Produse de calitate {brand_name.title()}"
        })
    
    # Sort by product count
    brands_data['brands'].sort(key=lambda x: x['product_count'], reverse=True)
    
    # Add statistics
    brands_data['statistics'] = {
        "most_products": brands_data['brands'][0]['name'] if brands_data['brands'] else "N/A",
        "countries_represented": len(set([b['origin'] for b in brands_data['brands'] if b['origin'] != "Unknown"])),
        "total_products": sum([b['product_count'] for b in brands_data['brands']])
    }
    
    # Save brands file
    with open('../data/brands.json', 'w', encoding='utf-8') as f:
        json.dump(brands_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created brands.json with {len(brands_data['brands'])} brands")

def main():
    """Main execution."""
    print("🔄 Generating category and brand files...")
    
    try:
        create_categories_file()
        create_brands_file()
        print("✅ All files generated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
