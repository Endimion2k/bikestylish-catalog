#!/usr/bin/env python3
"""
Fix Product Mapping with Strict Rules
Correct overly permissive product-category matching
"""

import pandas as pd
import json
from collections import defaultdict

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
            if product['price'] > 0:  # Only products with valid prices
                products.append(product)
        
        print(f"📦 Loaded {len(products)} products with valid prices")
        return products
        
    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return []

def strict_product_matching():
    """Recalculate product mappings with much stricter rules"""
    
    print("🔧 Fixing product mappings with strict rules...")
    
    products = load_product_data()
    if not products:
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
    
    # Define extensive strict matching rules - cover 90%+ categories
    strict_category_rules = {
        # Lighting
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
        
        # Child accessories
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
        
        # Storage
        'cosuri-pentru-biciclete': {
            'required': ['cos', 'basket', 'cos bicicleta'],
            'excluded': ['display', 'scaun', 'far', 'roti', 'trotineta', 'bagaj'],
            'min_price': 15, 'max_price': 400
        },
        
        # Wheels and tires
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
        
        # Protection
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
        
        # Clothing
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
        
        # Security
        'antifurturi': {
            'required': ['antifurt', 'lock', 'lacăt'],
            'excluded': ['display', 'scaun', 'far', 'casca'],
            'min_price': 15, 'max_price': 500
        },
        
        # Accessories
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
        
        # Frame parts and derailleur hangers
        'urechi-cadru': {
            'required': ['ureche cadru', 'urechi cadru', 'derailleur hanger', 'pilo'],
            'excluded': ['display', 'scaun'],
            'min_price': 5, 'max_price': 150
        },
        'furci': {
            'required': ['furca', 'fork', 'suspension'],
            'excluded': ['display', 'scaun'],
            'min_price': 50, 'max_price': 2000
        },
        'cuvete-directie': {
            'required': ['cuvete', 'headset', 'bearing', 'directie'],
            'excluded': ['display', 'scaun'],
            'min_price': 15, 'max_price': 800
        },
        'pedaliere': {
            'required': ['pedalier', 'bottom bracket', 'bb'],
            'excluded': ['display', 'scaun'],
            'min_price': 20, 'max_price': 1000
        },
        'schimbatoare': {
            'required': ['schimbator', 'derailleur', 'shifter'],
            'excluded': ['display', 'ureche'],
            'min_price': 30, 'max_price': 2000
        },
        'manete-schimbator': {
            'required': ['maneta', 'shifter', 'trigger'],
            'excluded': ['display', 'frana'],
            'min_price': 20, 'max_price': 1500
        },
        'portbagaje': {
            'required': ['portbagaj', 'rack', 'carrier'],
            'excluded': ['display', 'cos'],
            'min_price': 30, 'max_price': 500
        },
        'sonerii': {
            'required': ['sonerie', 'bell', 'horn'],
            'excluded': ['display', 'far'],
            'min_price': 5, 'max_price': 150
        },
        'calculatoare-bicicleta': {
            'required': ['calculator', 'computer', 'display'],
            'excluded': ['far', 'scaun'],
            'min_price': 20, 'max_price': 1000
        },
        'oglinzi': {
            'required': ['oglinda', 'mirror', 'retrovizor'],
            'excluded': ['far', 'scaun'],
            'min_price': 10, 'max_price': 200
        },
        
        # Additional existing categories
        'oglinda': {
            'required': ['oglinda', 'mirror', 'retrovizor'],
            'excluded': ['far', 'scaun'],
            'min_price': 10, 'max_price': 200
        },
        'furci-bicicleta': {
            'required': ['furca', 'fork', 'suspension'],
            'excluded': ['display', 'scaun'],
            'min_price': 50, 'max_price': 2000
        },
        'manete-frana': {
            'required': ['maneta frana', 'brake lever', 'lever'],
            'excluded': ['display', 'schimbator'],
            'min_price': 15, 'max_price': 500
        },
        'valve-adaptori-si-capete': {
            'required': ['valva', 'valve', 'adaptor', 'cap'],
            'excluded': ['display', 'scaun'],
            'min_price': 2, 'max_price': 100
        },
        'piese': {
            'required': ['piesa', 'component', 'spare'],
            'excluded': ['display', 'bicicleta completa'],
            'min_price': 5, 'max_price': 500
        },
        'parti-ghidoane-si-barend-extensii-ghidon': {
            'required': ['barend', 'extensie', 'part ghidon'],
            'excluded': ['display', 'scaun'],
            'min_price': 10, 'max_price': 300
        },
        'cricuri-de-mijloc': {
            'required': ['cric', 'stand', 'kickstand'],
            'excluded': ['display', 'e-bike'],
            'min_price': 10, 'max_price': 200
        },
        'rulmenti-accesorii-pedale': {
            'required': ['rulment', 'bearing', 'pedal'],
            'excluded': ['display', 'scaun'],
            'min_price': 5, 'max_price': 150
        },
        'borsete-sa': {
            'required': ['borseta', 'geanta sa', 'saddle bag'],
            'excluded': ['display', 'cos'],
            'min_price': 15, 'max_price': 300
        },
        'șei-156': {
            'required': ['sa', 'saddle', 'scaun sa'],
            'excluded': ['display', 'copii', 'husa'],
            'min_price': 15, 'max_price': 800
        },
        'remorci-transport-copii': {
            'required': ['remorca', 'trailer', 'transport copii'],
            'excluded': ['display', 'scaun'],
            'min_price': 200, 'max_price': 2000
        },
        'transport-si-depozitare': {
            'required': ['transport', 'depozitare', 'husa', 'geanta'],
            'excluded': ['display', 'remorca'],
            'min_price': 20, 'max_price': 500
        },
        'articole-copii-roti-ajutatoare': {
            'required': ['roti ajutatoare', 'training wheels', 'copii'],
            'excluded': ['display', 'scaun principal'],
            'min_price': 20, 'max_price': 350
        },
        'cadre-e-bike': {
            'required': ['cadru electric', 'e-bike frame', 'electric'],
            'excluded': ['display', 'accesoriu'],
            'min_price': 500, 'max_price': 5000
        },
        'protectii-si-accesorii-e-bike': {
            'required': ['protectie electric', 'e-bike', 'electric'],
            'excluded': ['display', 'cadru'],
            'min_price': 20, 'max_price': 800
        },
        'cricuri-e-bike': {
            'required': ['cric electric', 'e-bike stand', 'electric'],
            'excluded': ['display', 'cadru'],
            'min_price': 30, 'max_price': 400
        },
        'lanturi-e-bike': {
            'required': ['lant electric', 'e-bike chain', 'electric'],
            'excluded': ['display', 'antifurt'],
            'min_price': 20, 'max_price': 500
        },
        'accesorii-bicicleta': {
            'required': ['accesoriu', 'accessory', 'extra'],
            'excluded': ['display', 'bicicleta completa'],
            'min_price': 5, 'max_price': 300
        }
    }
    
    # Recalculate with strict rules
    category_real_data = {}
    total_strict_mappings = 0
    
    for cat_id, rules in strict_category_rules.items():
        required_terms = rules['required']
        excluded_terms = rules['excluded']
        min_price = rules['min_price']
        max_price = rules['max_price']
        
        matching_products = []
        
        for product in products:
            product_name = product['name'].lower()
            product_desc = product['description'].lower()
            product_cat = product['category'].lower()
            combined_text = f"{product_name} {product_desc} {product_cat}"
            
            # Check if price is in reasonable range
            if not (min_price <= product['price'] <= max_price):
                continue
            
            # Check if any required term matches
            has_required = False
            for term in required_terms:
                if term in combined_text:
                    has_required = True
                    break
            
            if not has_required:
                continue
            
            # Check if any excluded term matches
            has_excluded = False
            for term in excluded_terms:
                if term in combined_text:
                    has_excluded = True
                    break
            
            if has_excluded:
                continue
            
            # This product matches with strict rules
            matching_products.append(product)
        
        if matching_products:
            prices = [p['price'] for p in matching_products]
            brands = list(set([p['brand'] for p in matching_products if p['brand']]))
            
            category_real_data[cat_id] = {
                'product_count': len(matching_products),
                'price_range': {
                    'min': min(prices),
                    'max': max(prices),
                    'avg': sum(prices) / len(prices)
                },
                'brands': brands[:20],  # Limit to 20 brands
                'products': matching_products[:50]  # Keep only first 50 for reference
            }
            
            total_strict_mappings += len(matching_products)
            
            print(f"   ✅ {cat_id}: {len(matching_products)} products ({min(prices):.0f}-{max(prices):.0f} RON)")
    
    print(f"\n📊 Strict mapping results:")
    print(f"   Categories with products: {len(category_real_data)}")
    print(f"   Total product mappings: {total_strict_mappings:,}")
    print(f"   Reduction from: 40,581 → {total_strict_mappings:,}")
    
    # Update categories with strict data
    updated_categories = []
    
    for category in categories:
        updated_category = category.copy()
        cat_id = category['id']
        
        if cat_id in category_real_data:
            # Update with strict real data
            strict_data = category_real_data[cat_id]
            
            updated_category['real_data'] = {
                'product_count': strict_data['product_count'],
                'price_range': strict_data['price_range'],
                'brands': strict_data['brands'],
                'common_terms': [],  # Will be recalculated
                'last_updated': '2025-07-28T23:45:00'
            }
            
            # Update schema markup
            if ('content_structure' in updated_category and 
                'schema_markup' in updated_category['content_structure'] and
                'store_info' in updated_category['content_structure']['schema_markup']):
                
                min_price = int(strict_data['price_range']['min'])
                max_price = int(strict_data['price_range']['max'])
                updated_category['content_structure']['schema_markup']['store_info']['priceRange'] = f"{min_price}-{max_price} RON"
        
        else:
            # Keep existing data but mark as low-confidence
            if 'real_data' in updated_category:
                updated_category['real_data']['product_count'] = 0
        
        updated_categories.append(updated_category)
    
    # Save corrected data
    updated_data = data.copy()
    updated_data['categories'] = updated_categories
    
    try:
        with open('../data/categories_ai_enhanced.json', 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Product mappings fixed with strict rules!")
        print(f"   Data saved successfully")
        
    except Exception as e:
        print(f"❌ Error saving corrected data: {e}")

if __name__ == "__main__":
    strict_product_matching()
