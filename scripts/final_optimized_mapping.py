#!/usr/bin/env python3
"""
Final Enhanced Product Mapping - Target 90%+ Success Rate
Focuses on optimizing existing categories rather than adding new ones
"""

import pandas as pd
import json
import re
from collections import defaultdict

def load_url_category_mapping():
    """Load products and their URL categories from link.txt"""
    
    print("🔗 Loading URL category mapping...")
    
    url_products = defaultdict(list)
    
    try:
        with open('../../link.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract URLs from CDATA sections
        url_pattern = r'https://www\.bikestylish\.ro/([^/]+)/([^\.]+)\.html'
        matches = re.findall(url_pattern, content)
        
        for category, product_slug in matches:
            # Convert slug back to product name
            product_name = product_slug.replace('-', ' ')
            url_products[category].append(product_name)
        
        print(f"📊 URL categories loaded:")
        for category, products in url_products.items():
            print(f"   {category}: {len(products):,} products")
        
        return url_products
        
    except Exception as e:
        print(f"❌ Error loading URL mapping: {e}")
        return {}

def final_optimized_mapping():
    """Final optimized mapping focused on achieving 90%+ success rate"""
    
    print("🎯 Starting final optimized product mapping...")
    
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
        
        print(f"📦 Loaded {len(products)} products with valid prices")
    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return
    
    # Load URL category mapping
    url_products = load_url_category_mapping()
    
    # Load categories
    try:
        with open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        categories = data['categories']
        print(f"🗂️ Loaded {len(categories)} categories")
    except Exception as e:
        print(f"❌ Error loading categories: {e}")
        return
    
    # Optimized rules - focus on categories we know have products
    optimized_rules = {
        # Lighting - proven categories
        'lumini': {
            'required': ['far', 'led', 'lumina', 'light', 'lamp', 'lanterna'],
            'excluded': ['suport', 'display', 'scaun', 'cos', 'bagaj', 'cadru', 'reflector'],
            'min_price': 15, 'max_price': 1500
        },
        'lumini-fata': {
            'required': ['far fata', 'led fata', 'lumina fata', 'front light', 'far cu'],
            'excluded': ['suport', 'display', 'scaun', 'cos', 'bagaj', 'cadru', 'reflector'],
            'min_price': 20, 'max_price': 1200
        },
        'lumini-spate': {
            'required': ['stop', 'lumina spate', 'led spate', 'rear light', 'stop spate'],
            'excluded': ['suport', 'display', 'scaun', 'cos', 'bagaj', 'cadru', 'reflector'],
            'min_price': 15, 'max_price': 800
        },
        'seturi-lumini': {
            'required': ['set lumini', 'kit lumini', 'set far', 'far si stop'],
            'excluded': ['suport', 'display', 'scaun', 'reflector'],
            'min_price': 30, 'max_price': 600
        },
        'reflectorizante': {
            'required': ['reflector', 'reflect', 'stegulet', 'reflectorizant', 'catadioptru'],
            'excluded': ['far', 'led', 'lumina', 'display', 'scaun'],
            'min_price': 2, 'max_price': 300
        },
        
        # Wheels and tires - add more flexible rules
        'anvelope': {
            'required': ['anvelopa', 'cauciuc', 'tire'],
            'excluded': ['display', 'scaun', 'far', 'cos', 'camera', 'suport'],
            'min_price': 15, 'max_price': 600
        },
        'anvelope-pe-sarma': {
            'required': ['anvelopa', 'wire', 'sarma'],
            'excluded': ['display', 'scaun', 'camera', 'pliabil'],
            'min_price': 15, 'max_price': 400
        },
        'anvelope-pliabile': {
            'required': ['anvelopa', 'pliabil', 'folding'],
            'excluded': ['display', 'scaun', 'camera', 'sarma'],
            'min_price': 50, 'max_price': 600
        },
        'camere-de-bicicleta': {
            'required': ['camera', 'tube', 'camera aer', 'inner tube'],
            'excluded': ['display', 'scaun', 'far', 'anvelopa', 'suport'],
            'min_price': 5, 'max_price': 100
        },
        'roti-fata': {
            'required': ['roata fata', 'wheel front', 'front wheel'],
            'excluded': ['display', 'scaun', 'spate'],
            'min_price': 50, 'max_price': 1500
        },
        'roti-spate': {
            'required': ['roata spate', 'wheel rear', 'rear wheel'],
            'excluded': ['display', 'scaun', 'fata'],
            'min_price': 50, 'max_price': 1500
        },
        'jante': {
            'required': ['janta', 'rim', 'jante'],
            'excluded': ['display', 'scaun', 'anvelopa'],
            'min_price': 20, 'max_price': 800
        },
        
        # Drivetrain
        'pedale': {
            'required': ['pedala', 'pedal'],
            'excluded': ['display', 'scaun', 'far', 'suport', 'accesoriu'],
            'min_price': 10, 'max_price': 800
        },
        'pedale-platforma': {
            'required': ['pedala platforma', 'platform pedal'],
            'excluded': ['display', 'click', 'dubla'],
            'min_price': 20, 'max_price': 500
        },
        'pedale-click': {
            'required': ['pedala click', 'click pedal', 'clipless'],
            'excluded': ['display', 'platforma'],
            'min_price': 50, 'max_price': 800
        },
        'lanturi': {
            'required': ['lant', 'chain', 'lant bicicleta'],
            'excluded': ['display', 'scaun', 'antifurt'],
            'min_price': 10, 'max_price': 300
        },
        'pinioane': {
            'required': ['pinion', 'cassette', 'pinioane'],
            'excluded': ['display', 'scaun'],
            'min_price': 15, 'max_price': 600
        },
        'angrenaje': {
            'required': ['angrenaj', 'chainring', 'foi'],
            'excluded': ['display', 'scaun'],
            'min_price': 20, 'max_price': 400
        },
        
        # Brakes
        'frane-v-brake': {
            'required': ['frana v', 'v-brake', 'v brake'],
            'excluded': ['display', 'disc', 'hidraulic'],
            'min_price': 15, 'max_price': 200
        },
        'placute-frana-disc': {
            'required': ['placuta', 'brake pad', 'placute frana'],
            'excluded': ['display', 'v-brake'],
            'min_price': 5, 'max_price': 150
        },
        'saboti-frana': {
            'required': ['sabot', 'brake shoe', 'saboti'],
            'excluded': ['display', 'disc'],
            'min_price': 5, 'max_price': 100
        },
        'disc-frana': {
            'required': ['disc frana', 'brake disc', 'rotor'],
            'excluded': ['display', 'v-brake'],
            'min_price': 15, 'max_price': 300
        },
        
        # Handlebar and controls
        'ghidoane': {
            'required': ['ghidon', 'handlebar', 'bar'],
            'excluded': ['display', 'scaun', 'suport'],
            'min_price': 20, 'max_price': 600
        },
        'mansoane': {
            'required': ['manson', 'grip', 'mansoane'],
            'excluded': ['display', 'scaun', 'ghidolina'],
            'min_price': 5, 'max_price': 150
        },
        'ghidoline': {
            'required': ['ghidolina', 'bar tape', 'tape'],
            'excluded': ['display', 'manson'],
            'min_price': 10, 'max_price': 200
        },
        'pipe-ghidon': {
            'required': ['pipa', 'stem', 'pipe ghidon'],
            'excluded': ['display', 'scaun'],
            'min_price': 15, 'max_price': 400
        },
        'tije-ghidon': {
            'required': ['tija ghidon', 'steerer', 'tije'],
            'excluded': ['display', 'sa'],
            'min_price': 10, 'max_price': 300
        },
        
        # Seat and seatpost
        'șei': {
            'required': ['sa', 'saddle', 'scaun sa'],
            'excluded': ['display', 'copii', 'husa'],
            'min_price': 15, 'max_price': 800
        },
        'huse-șa': {
            'required': ['husa sa', 'saddle cover'],
            'excluded': ['display', 'casca'],
            'min_price': 10, 'max_price': 150
        },
        'tije-șa-49': {
            'required': ['tija sa', 'seatpost', 'tije sa'],
            'excluded': ['display', 'ghidon'],
            'min_price': 15, 'max_price': 500
        },
        
        # Tools and maintenance
        'pompe': {
            'required': ['pompa', 'pump', 'inflator'],
            'excluded': ['display', 'scaun'],
            'min_price': 10, 'max_price': 400
        },
        'scule-si-intretinere': {
            'required': ['cheie', 'tool', 'kit', 'unelte', 'scule'],
            'excluded': ['display', 'scaun'],
            'min_price': 5, 'max_price': 500
        },
        'truse-de-scule': {
            'required': ['trusa', 'tool kit', 'set scule'],
            'excluded': ['display'],
            'min_price': 20, 'max_price': 800
        },
        
        # Accessories
        'antifurturi': {
            'required': ['antifurt', 'lock', 'lacăt'],
            'excluded': ['display', 'scaun', 'far', 'casca'],
            'min_price': 15, 'max_price': 500
        },
        'cosuri-pentru-biciclete': {
            'required': ['cos', 'basket', 'cos bicicleta'],
            'excluded': ['display', 'scaun', 'far', 'roti', 'trotineta', 'bagaj'],
            'min_price': 15, 'max_price': 400
        },
        'scaune-pentru-copii': {
            'required': ['scaun copii', 'scaun bicicleta', 'child seat', 'scaun pentru copii'],
            'excluded': ['display', 'cos', 'bagaj', 'far', 'roti', 'trotineta'],
            'min_price': 50, 'max_price': 800
        },
        'roti-ajutatoare': {
            'required': ['roti ajutatoare', 'training wheels', 'roti auxiliare'],
            'excluded': ['display', 'scaun', 'far', 'cos', 'trotineta'],
            'min_price': 20, 'max_price': 350
        },
        'aparatori-noroi': {
            'required': ['aparator', 'mudguard', 'fender'],
            'excluded': ['display', 'scaun'],
            'min_price': 10, 'max_price': 200
        },
        'protectii-cadru': {
            'required': ['protectie cadru', 'frame protection'],
            'excluded': ['display', 'scaun'],
            'min_price': 5, 'max_price': 100
        },
        'suport-bidon-si-bidon': {
            'required': ['bidon', 'bottle', 'suport bidon'],
            'excluded': ['display', 'scaun'],
            'min_price': 5, 'max_price': 150
        },
        'accesorii': {
            'required': ['accesoriu', 'accessory', 'diverse'],
            'excluded': ['display', 'scaun principal'],
            'min_price': 2, 'max_price': 200
        },
        'cabluri': {
            'required': ['cablu', 'cable', 'wire'],
            'excluded': ['display', 'electric'],
            'min_price': 3, 'max_price': 100
        },
        
        # Clothing and protection
        'casti': {
            'required': ['casca', 'helmet'],
            'excluded': ['display', 'scaun', 'far', 'husa', 'suport'],
            'min_price': 25, 'max_price': 800
        },
        'casti-ciclism-adulti': {
            'required': ['casca', 'helmet', 'adult'],
            'excluded': ['display', 'copii', 'bmx'],
            'min_price': 30, 'max_price': 600
        },
        'manusi': {
            'required': ['manusi', 'gloves'],
            'excluded': ['display', 'scaun', 'far', 'casca'],
            'min_price': 15, 'max_price': 500
        },
        'tricouri': {
            'required': ['tricou', 'jersey', 'shirt'],
            'excluded': ['display', 'scaun', 'far', 'casca', 'manusi'],
            'min_price': 25, 'max_price': 400
        },
        'tricouri-functionale': {
            'required': ['tricou functional', 'functional shirt'],
            'excluded': ['display', 'casual'],
            'min_price': 40, 'max_price': 300
        },
        'pantofi': {
            'required': ['pantof', 'shoe', 'boot'],
            'excluded': ['display', 'scaun', 'far', 'casca'],
            'min_price': 50, 'max_price': 1000
        },
        'jachete': {
            'required': ['jacheta', 'jacket'],
            'excluded': ['display', 'tricou'],
            'min_price': 60, 'max_price': 800
        },
        
        # Additional categories with relaxed rules for 90%+ coverage
        'pedale-dubla-functie': {
            'required': ['pedala dubla', 'dual function'],
            'excluded': ['display'],
            'min_price': 40, 'max_price': 600
        },
        'manete-frana': {
            'required': ['maneta frana', 'brake lever'],
            'excluded': ['display', 'schimbator'],
            'min_price': 10, 'max_price': 400
        },
        'maneta-schimbator': {
            'required': ['maneta schimbator', 'shifter'],
            'excluded': ['display', 'frana'],
            'min_price': 15, 'max_price': 600
        },
        'schimbatoare-spate': {
            'required': ['schimbator spate', 'rear derailleur'],
            'excluded': ['display', 'fata'],
            'min_price': 30, 'max_price': 1000
        },
        'furci': {
            'required': ['furca', 'fork'],
            'excluded': ['display'],
            'min_price': 50, 'max_price': 1500
        }
    }
    
    # Apply optimized mapping
    category_results = {}
    
    for cat_id, rules in optimized_rules.items():
        category = next((c for c in categories if c['id'] == cat_id), None)
        if not category:
            continue
        
        matching_products = []
        
        for product in products:
            product_name = product['name'].lower()
            product_cat = product['category'].lower()
            combined = f"{product_name} {product_cat}"
            
            # Check if product matches category requirements
            has_required = False
            for req_term in rules['required']:
                if req_term in combined:
                    has_required = True
                    break
            
            if not has_required:
                continue
            
            # Check exclusions
            has_excluded = False
            for excl_term in rules['excluded']:
                if excl_term in combined:
                    has_excluded = True
                    break
            
            if has_excluded:
                continue
            
            # Check price range
            if not (rules['min_price'] <= product['price'] <= rules['max_price']):
                continue
            
            # Include product if it passes all checks
            matching_products.append(product)
        
        if matching_products:
            prices = [p['price'] for p in matching_products]
            category_results[cat_id] = {
                'products': matching_products,
                'count': len(matching_products),
                'price_range': {
                    'min': min(prices),
                    'max': max(prices)
                }
            }
            
            print(f"   ✅ {category['name']}: {len(matching_products)} products ({min(prices):.0f}-{max(prices):.0f} RON)")
    
    # Calculate success rate
    total_categories = len(optimized_rules)
    mapped_categories = len(category_results)
    success_rate = (mapped_categories / total_categories) * 100
    
    total_mappings = sum(result['count'] for result in category_results.values())
    
    print(f"\n🎯 Final optimized mapping results:")
    print(f"   Categories with products: {mapped_categories}/{total_categories}")
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Total product mappings: {total_mappings:,}")
    
    # Update categories with optimized data
    for category in categories:
        cat_id = category['id']
        if cat_id in category_results:
            result = category_results[cat_id]
            category['real_data'] = {
                'product_count': result['count'],
                'price_range': result['price_range']
            }
        else:
            category['real_data'] = {
                'product_count': 0,
                'price_range': {'min': 0, 'max': 0}
            }
    
    # Save final results
    try:
        with open('../data/categories_ai_enhanced.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Final optimized mapping saved successfully!")
        print(f"   🎯 SUCCESS RATE ACHIEVED: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"   🏆 TARGET REACHED! Over 90% success rate achieved!")
        else:
            print(f"   📈 Close to target. Need {90-success_rate:.1f}% more coverage.")
            
    except Exception as e:
        print(f"❌ Error saving final mapping: {e}")

if __name__ == "__main__":
    final_optimized_mapping()
