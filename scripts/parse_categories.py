#!/usr/bin/env python3
"""
Parse categories from sitemap and add to catalog structure
"""

import json
import re
from typing import List, Dict

def parse_categories_sitemap():
    """Parse categories from categorii.txt sitemap."""
    
    print("📂 Parsing categories from sitemap...")
    
    categories = []
    
    try:
        with open('../categorii.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all URLs from sitemap
        url_pattern = r'<loc>(https://www\.bikestylish\.ro/[^<]+)</loc>'
        urls = re.findall(url_pattern, content)
        
        print(f"🔗 Found {len(urls)} category URLs")
        
        for url in urls:
            # Extract category name from URL
            category_path = url.replace('https://www.bikestylish.ro/', '')
            
            # Clean category name
            category_name = category_path.replace('-', ' ').replace('_', ' ')
            category_name = ' '.join(word.capitalize() for word in category_name.split())
            
            # Determine category type and parent
            category_type = determine_category_type(category_path)
            parent_category = determine_parent_category(category_path)
            
            category = {
                "id": category_path,
                "name": category_name,
                "url": url,
                "type": category_type,
                "parent": parent_category,
                "priority": 0.8,
                "last_modified": "2025-07-28"
            }
            
            categories.append(category)
        
        return categories
        
    except Exception as e:
        print(f"❌ Error parsing categories: {e}")
        return []

def determine_category_type(category_path: str) -> str:
    """Determine category type based on path."""
    
    if any(term in category_path for term in ['accesorii', 'lumini', 'protectii', 'transport']):
        return 'accesorii'
    elif any(term in category_path for term in ['piese', 'anvelope', 'jante', 'lanturi', 'frane']):
        return 'piese'
    elif any(term in category_path for term in ['echipament', 'casti', 'manusi', 'tricouri', 'pantofi']):
        return 'echipament'
    elif any(term in category_path for term in ['scule', 'intretinere', 'unelte']):
        return 'scule'
    elif any(term in category_path for term in ['e-bike', 'cadre-e-bike', 'protectii-si-accesorii-e-bike']):
        return 'e-bike'
    elif any(term in category_path for term in ['copii', 'roti-ajutatoare', 'scaune-pentru-copii']):
        return 'copii'
    else:
        return 'general'

def determine_parent_category(category_path: str) -> str:
    """Determine parent category."""
    
    if category_path in ['accesorii', 'accesorii-bicicleta']:
        return None
    elif category_path == 'piese':
        return None
    elif category_path == 'echipament':
        return None
    elif 'accesorii' in category_path or any(term in category_path for term in ['lumini', 'cosuri', 'protectii-cadru']):
        return 'accesorii'
    elif any(term in category_path for term in ['anvelope', 'jante', 'lanturi', 'frane', 'schimbator']):
        return 'piese'
    elif any(term in category_path for term in ['casti', 'manusi', 'tricouri', 'pantofi', 'jachete']):
        return 'echipament'
    else:
        return None

def create_hierarchical_categories(categories: List[Dict]) -> Dict:
    """Create hierarchical category structure."""
    
    # Group by parent
    hierarchy = {
        "main_categories": [],
        "subcategories": {},
        "category_tree": {}
    }
    
    # Find main categories (no parent)
    main_cats = [cat for cat in categories if cat['parent'] is None]
    subcats = [cat for cat in categories if cat['parent'] is not None]
    
    # Build hierarchy
    for main_cat in main_cats:
        main_id = main_cat['id']
        hierarchy["main_categories"].append(main_cat)
        hierarchy["subcategories"][main_id] = []
        
        # Find subcategories
        for subcat in subcats:
            if subcat['parent'] == main_cat['type']:
                hierarchy["subcategories"][main_id].append(subcat)
    
    return hierarchy

def generate_category_mappings(categories: List[Dict]) -> Dict:
    """Generate category mappings for product classification."""
    
    mappings = {
        "url_to_category": {},
        "name_to_id": {},
        "type_groups": {},
        "search_terms": {}
    }
    
    for category in categories:
        cat_id = category['id']
        cat_name = category['name']
        cat_type = category['type']
        cat_url = category['url']
        
        # URL mapping
        mappings["url_to_category"][cat_url] = cat_id
        
        # Name mapping  
        mappings["name_to_id"][cat_name.lower()] = cat_id
        
        # Type grouping
        if cat_type not in mappings["type_groups"]:
            mappings["type_groups"][cat_type] = []
        mappings["type_groups"][cat_type].append(cat_id)
        
        # Search terms
        search_terms = generate_category_search_terms(cat_id, cat_name)
        mappings["search_terms"][cat_id] = search_terms
    
    return mappings

def generate_category_search_terms(cat_id: str, cat_name: str) -> List[str]:
    """Generate search terms for category."""
    
    terms = []
    
    # Base terms from ID and name
    terms.extend(cat_id.split('-'))
    terms.extend(cat_name.lower().split())
    
    # Add specific terms based on category
    if 'lumini' in cat_id:
        terms.extend(['led', 'light', 'far', 'stop', 'iluminat'])
    elif 'anvelope' in cat_id:
        terms.extend(['tire', 'wheel', 'rubber', 'cauciuc'])
    elif 'casti' in cat_id:
        terms.extend(['helmet', 'protection', 'safety', 'casca'])
    elif 'manusi' in cat_id:
        terms.extend(['gloves', 'hands', 'grip'])
    elif 'e-bike' in cat_id:
        terms.extend(['electric', 'battery', 'motor', 'electric'])
    
    return list(set(terms))  # Remove duplicates

def update_catalog_with_categories():
    """Update main catalog with parsed categories."""
    
    print("🔄 Updating catalog with categories...")
    
    # Parse categories from sitemap
    categories = parse_categories_sitemap()
    
    if not categories:
        print("❌ No categories found")
        return
    
    print(f"📂 Parsed {len(categories)} categories")
    
    # Create hierarchy
    hierarchy = create_hierarchical_categories(categories)
    
    # Generate mappings
    mappings = generate_category_mappings(categories)
    
    # Load existing catalog
    try:
        with open('../data/products_ai_enhanced.json', 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    except:
        with open('../data/products.json', 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    
    # Update catalog with categories
    catalog['categories_detailed'] = {
        "total_categories": len(categories),
        "hierarchy": hierarchy,
        "mappings": mappings,
        "all_categories": categories
    }
    
    # Add category enhancement to AI optimization
    if 'ai_optimization' not in catalog:
        catalog['ai_optimization'] = {}
    
    catalog['ai_optimization']['category_features'] = {
        "hierarchical_structure": True,
        "url_mappings": True,
        "search_optimization": True,
        "parent_child_relationships": True,
        "multilingual_terms": True
    }
    
    # Save enhanced catalog
    with open('../data/products_ai_enhanced.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    # Create separate categories file
    categories_data = {
        "last_updated": "2025-07-28T23:00:00.000000",
        "total_categories": len(categories),
        "source": "bikestylish.ro sitemap",
        "hierarchy": hierarchy,
        "mappings": mappings,
        "categories": categories
    }
    
    with open('../data/categories_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(categories_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Catalog updated with detailed categories!")
    
    # Show statistics
    print(f"\n📊 Category Statistics:")
    print(f"   Total categories: {len(categories)}")
    print(f"   Main categories: {len(hierarchy['main_categories'])}")
    print(f"   Category types: {len(mappings['type_groups'])}")
    
    # Show sample categories by type
    for cat_type, cat_list in mappings['type_groups'].items():
        print(f"   {cat_type.capitalize()}: {len(cat_list)} categories")
    
    # Show sample categories
    print(f"\n📋 Sample Categories:")
    for i, category in enumerate(categories[:5]):
        print(f"   {i+1}. {category['name']}")
        print(f"      ID: {category['id']}")
        print(f"      Type: {category['type']}")
        print(f"      URL: {category['url'][:60]}...")

if __name__ == "__main__":
    update_catalog_with_categories()
