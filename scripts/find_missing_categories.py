#!/usr/bin/env python3
"""
Find missing categories by analyzing URL structure and current mapping
"""

import pandas as pd
import re
from collections import defaultdict

def find_missing_categories():
    """Find categories that exist in URLs but are missing from our mapping"""
    
    print("🔍 Finding missing categories...")
    
    # Load all products
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
    
    # Load URL data
    with open('../../link.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract URLs from CDATA sections
    url_pattern = r'https://www\.bikestylish\.ro/([^/]+)/([^\.]+)\.html'
    matches = re.findall(url_pattern, content)
    
    url_products = {}
    for cat, prod in matches:
        product_name = prod.replace('-', ' ')
        url_products[product_name.lower()] = cat
    
    print(f"🔗 Found {len(url_products)} products in URLs")
    
    # Current categories with strict rules
    current_categories = {
        'lumini', 'lumini-fata', 'lumini-spate', 'seturi-lumini', 'reflectorizante',
        'scaune-pentru-copii', 'roti-ajutatoare', 'cosuri-pentru-biciclete',
        'anvelope', 'anvelope-pe-sarma', 'anvelope-pliabile', 'camere-de-bicicleta',
        'roti-fata', 'roti-spate', 'jante', 'pedale', 'pedale-click', 'lanturi',
        'pinioane', 'angrenaje', 'frane-v-brake', 'placute-frana-disc', 'saboti-frana',
        'disc-frana', 'ghidoane', 'mansoane', 'ghidoline', 'pipe-ghidon', 'tije-ghidon',
        'șei', 'huse-șa', 'tije-șa-49', 'pompe', 'scule-si-intretinere', 'truse-de-scule',
        'casti', 'casti-ciclism-adulti', 'aparatori-noroi', 'protectii-cadru', 'manusi',
        'tricouri', 'tricouri-functionale', 'pantofi', 'jachete', 'antifurturi',
        'suport-bidon-si-bidon', 'accesorii', 'cabluri'
    }
    
    # Analyze products that might fit missing categories
    potential_categories = defaultdict(list)
    
    # Look for specific keywords that might indicate missing categories
    missing_keywords = [
        'ureche', 'urechi', 'frame', 'cadru',
        'derailleur', 'schimbator', 'shifter',
        'suspension', 'amortizor', 'fork',
        'brake', 'frana', 'caliper',
        'stem', 'pipa', 'spacer',
        'headset', 'cuvete', 'bearing',
        'bottom bracket', 'pedalier',
        'rack', 'portbagaj', 'carrier',
        'mudguard', 'aparator',
        'computer', 'calculator', 'display',
        'bell', 'sonerie', 'horn',
        'mirror', 'oglinda', 'retrovizor'
    ]
    
    for product in products:
        product_name = product['name'].lower()
        product_cat = product['category'].lower()
        combined = f"{product_name} {product_cat}"
        
        # Check for missing keywords
        for keyword in missing_keywords:
            if keyword in combined:
                potential_categories[keyword].append({
                    'name': product['name'][:60],
                    'price': product['price'],
                    'category': product['category']
                })
    
    print(f"\n🔍 Potential missing categories:")
    for keyword, prods in potential_categories.items():
        if len(prods) >= 3:  # Only show if at least 3 products
            prices = [p['price'] for p in prods]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            
            print(f"\n📂 {keyword.upper()} ({len(prods)} products)")
            print(f"   Price range: {min_price:.0f} - {max_price:.0f} RON (avg: {avg_price:.0f})")
            print(f"   Sample products:")
            for i, prod in enumerate(prods[:5]):
                print(f"      {i+1}. {prod['name']}... - {prod['price']:.0f} RON")
    
    # Check for "ureche-cadru" specifically
    ureche_products = []
    for product in products:
        if 'ureche' in product['name'].lower() or 'urechi' in product['name'].lower():
            ureche_products.append(product)
    
    print(f"\n🔍 URECHE-CADRU products found: {len(ureche_products)}")
    for product in ureche_products:
        print(f"   - {product['name']} - {product['price']:.0f} RON (cat: {product['category']})")
    
    # Find what URL category they belong to
    if ureche_products:
        for product in ureche_products:
            product_url_name = product['name'].lower().replace(' ', ' ')
            for url_name, url_cat in url_products.items():
                if 'ureche' in url_name:
                    print(f"   URL: {url_cat}/{url_name}")

if __name__ == "__main__":
    find_missing_categories()
