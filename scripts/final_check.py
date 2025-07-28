#!/usr/bin/env python3
"""
Final Check Script - Verificare completare procesare categorii
"""

import json
import sys
from datetime import datetime

def load_json():
    """Încarcă JSON-ul cu categoriile"""
    try:
        with open('../categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Fișierul categories_ai_enhanced.json nu a fost găsit!")
        return None
    except json.JSONDecodeError:
        print("❌ Fișierul JSON este corupt!")
        return None

def check_completion(data):
    """Verifică ce categorii au fost procesate"""
    if not data or 'categories' not in data:
        print("❌ Structura JSON nu este validă!")
        return
    
    categories = data['categories']
    total_categories = len(categories)
    processed_categories = []
    unprocessed_categories = []
    
    for category_id, category_data in categories.items():
        if 'real_data' in category_data and category_data['real_data']:
            # Verifică dacă are date reale
            real_data = category_data['real_data']
            if ('product_count' in real_data and 
                real_data['product_count'] is not None and 
                real_data['product_count'] > 0):
                processed_categories.append(category_id)
            else:
                unprocessed_categories.append(category_id)
        else:
            unprocessed_categories.append(category_id)
    
    # Statistici
    processed_count = len(processed_categories)
    unprocessed_count = len(unprocessed_categories)
    completion_percentage = (processed_count / total_categories) * 100
    
    print("=" * 60)
    print("🔍 RAPORT FINAL PROCESARE CATEGORII")
    print("=" * 60)
    print(f"📊 Total categorii: {total_categories}")
    print(f"✅ Procesate: {processed_count}")
    print(f"⏳ Rămase: {unprocessed_count}")
    print(f"📈 Progres: {completion_percentage:.1f}%")
    print()
    
    if processed_count > 0:
        print("✅ CATEGORII PROCESATE:")
        for i, cat_id in enumerate(processed_categories, 1):
            category_data = categories[cat_id]
            product_count = category_data.get('real_data', {}).get('product_count', 0)
            print(f"   {i:2d}. {cat_id} ({product_count} produse)")
        print()
    
    if unprocessed_count > 0:
        print("⏳ CATEGORII RĂMASE DE PROCESAT:")
        for i, cat_id in enumerate(unprocessed_categories, 1):
            category_name = categories[cat_id].get('name', cat_id)
            print(f"   {i:2d}. {cat_id} - {category_name}")
        print()
        
        print("🚀 Pentru a continua procesarea, rulează:")
        print("   python run_auto_update.py")
        print()
    else:
        print("🎉 FELICITĂRI! Toate categoriile au fost procesate!")
        print("✨ JSON-ul este complet actualizat cu date reale!")
        print()
    
    return completion_percentage >= 100

def generate_summary(data):
    """Generează un sumar al datelor procesate"""
    if not data or 'categories' not in data:
        return
    
    categories = data['categories']
    total_products = 0
    all_brands = set()
    price_ranges = []
    
    for category_id, category_data in categories.items():
        if 'real_data' in category_data and category_data['real_data']:
            real_data = category_data['real_data']
            
            # Produse
            if 'product_count' in real_data:
                total_products += real_data['product_count'] or 0
            
            # Mărci
            if 'brands' in real_data and real_data['brands']:
                all_brands.update(real_data['brands'])
            
            # Prețuri
            if 'price_range' in real_data and real_data['price_range']:
                pr = real_data['price_range']
                if 'min' in pr and 'max' in pr:
                    price_ranges.append((pr['min'], pr['max']))
    
    if total_products > 0:
        print("📈 SUMAR GENERAL:")
        print(f"   🛍️  Total produse: {total_products:,}")
        print(f"   🏷️  Total mărci: {len(all_brands)}")
        
        if price_ranges:
            min_price = min(pr[0] for pr in price_ranges if pr[0] is not None)
            max_price = max(pr[1] for pr in price_ranges if pr[1] is not None)
            print(f"   💰 Interval prețuri: {min_price:.0f} - {max_price:.0f} RON")
        
        print(f"   📅 Ultimul update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def main():
    """Funcția principală"""
    print("🔍 Verificare finală procesare categorii BikeStylish...")
    print()
    
    # Încarcă datele
    data = load_json()
    if not data:
        sys.exit(1)
    
    # Verifică completarea
    is_complete = check_completion(data)
    
    # Generează sumarul
    generate_summary(data)
    
    if is_complete:
        print("🎯 STATUS: PROCESARE COMPLETĂ! ✅")
    else:
        print("⚠️  STATUS: PROCESARE ÎN CURS... ⏳")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
