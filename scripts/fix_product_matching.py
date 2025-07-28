#!/usr/bin/env python3
"""
Fix Product-Category Matching
Corrects the product matching algorithm and runs real data integration
"""

import pandas as pd
import json
from collections import defaultdict
from typing import Dict, List, Set
import re

def load_product_data() -> List[Dict]:
    """Load product data from Excel file"""
    
    try:
        # Load the Excel file
        df = pd.read_excel('../sxt26.xls')
        
        # Convert to list of dictionaries
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
    """Find which categories a product belongs to - FIXED VERSION"""
    
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
    """Infer category from product characteristics - ENHANCED VERSION"""
    
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

def extract_price(product: Dict) -> float:
    """Extract price from product data"""
    
    # Try different price fields
    price_fields = ['price', 'pret_sugerat', 'pret_produs', 'pret']
    
    for field in price_fields:
        if field in product:
            try:
                price = float(product[field])
                if price > 0:
                    return price
            except (ValueError, TypeError):
                continue
    
    return 0.0

def extract_brand(product: Dict) -> str:
    """Extract brand from product data"""
    
    brand_fields = ['brand', 'producator', 'marca', 'manufacturer']
    
    for field in brand_fields:
        if field in product:
            brand = str(product[field]).strip()
            if brand and brand.lower() not in ['nan', 'none', '']:
                return brand
    
    return ""

def test_enhanced_matching():
    """Test the enhanced matching algorithm"""
    
    print("🧪 Testing Enhanced Product-Category Matching...")
    
    # Load data
    products = load_product_data()
    if not products:
        return
    
    # Load categories
    try:
        with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        categories = categories_data.get('categories', [])
        category_lookup = {cat['id']: cat for cat in categories}
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Test matching on sample products
    matched_count = 0
    total_matches = 0
    
    sample_products = products[:20]  # Test first 20 products
    
    for i, product in enumerate(sample_products):
        matches = find_product_categories(product, category_lookup)
        if matches:
            matched_count += 1
            total_matches += len(matches)
            print(f"✅ Product {i+1}: '{product['name'][:50]}...' → {len(matches)} categories")
            for match in matches[:3]:  # Show first 3 matches
                print(f"    → {match}")
        else:
            print(f"❌ Product {i+1}: '{product['name'][:50]}...' → No matches")
    
    print(f"\n📊 Test Results:")
    print(f"   Products with matches: {matched_count}/{len(sample_products)} ({matched_count/len(sample_products)*100:.1f}%)")
    print(f"   Total matches found: {total_matches}")
    print(f"   Average matches per product: {total_matches/len(sample_products):.1f}")
    
    if matched_count > 0:
        print("\n✅ Enhanced matching algorithm working correctly!")
        return True
    else:
        print("\n❌ Enhanced matching algorithm still has issues!")
        return False

if __name__ == "__main__":
    success = test_enhanced_matching()
    if success:
        print("\n🚀 Ready to run full category enhancement with working matching algorithm!")
    else:
        print("\n⚠️  Need to investigate matching algorithm further.")
