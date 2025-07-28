#!/usr/bin/env python3
"""
Script pentru monitorizarea progresului actualizării categoriilor.
Afișează statistici despre categoriile procesate și cele rămase.
"""

import json
from datetime import datetime
import sys

def load_categories(json_file):
    """Încarcă categoriile din JSON"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Eroare la încărcarea JSON: {e}")
        return None

def analyze_categories(data):
    """Analizează progresul categoriilor"""
    if not data or 'categories' not in data:
        return
    
    categories = data['categories']
    total_categories = len(categories)
    processed_count = 0
    total_products = 0
    
    processed_categories = []
    unprocessed_categories = []
    
    for category in categories:
        real_data = category.get('real_data', {})
        
        # Verifică dacă categoria a fost procesată recent (cu date reale)
        if (real_data.get('last_updated', '').startswith('2025-01-15') or
            real_data.get('last_updated', '').startswith('2025-07-29')):
            processed_count += 1
            total_products += real_data.get('product_count', 0)
            processed_categories.append({
                'id': category['id'],
                'name': category['name'],
                'url': category['url'],
                'product_count': real_data.get('product_count', 0),
                'brands': len(real_data.get('brands', [])),
                'last_updated': real_data.get('last_updated', 'N/A')
            })
        else:
            unprocessed_categories.append({
                'id': category['id'],
                'name': category['name'],
                'url': category['url']
            })
    
    return {
        'total_categories': total_categories,
        'processed_count': processed_count,
        'unprocessed_count': total_categories - processed_count,
        'total_products': total_products,
        'processed_categories': processed_categories,
        'unprocessed_categories': unprocessed_categories
    }

def print_report(stats):
    """Afișează raportul de progres"""
    print("=" * 60)
    print("📊 RAPORT PROGRES ACTUALIZARE CATEGORII BIKESTYLISH")
    print("=" * 60)
    
    print(f"\n📈 PROGRES GENERAL:")
    print(f"   • Total categorii: {stats['total_categories']}")
    print(f"   • Procesate: {stats['processed_count']}")
    print(f"   • Rămase: {stats['unprocessed_count']}")
    print(f"   • Progres: {(stats['processed_count']/stats['total_categories']*100):.1f}%")
    print(f"   • Total produse procesate: {stats['total_products']}")
    
    print(f"\n✅ CATEGORII PROCESATE ({stats['processed_count']}):")
    for cat in stats['processed_categories']:
        print(f"   • {cat['name']} ({cat['id']})")
        print(f"     └─ {cat['product_count']} produse, {cat['brands']} mărci")
    
    print(f"\n⏳ CATEGORII RĂMASE ({stats['unprocessed_count']}):")
    for i, cat in enumerate(stats['unprocessed_categories'][:10], 1):  # Primele 10
        print(f"   {i:2d}. {cat['name']} ({cat['id']})")
        print(f"       └─ {cat['url']}")
    
    if stats['unprocessed_count'] > 10:
        print(f"   ... și încă {stats['unprocessed_count'] - 10} categorii")
    
    print(f"\n🎯 URMĂTOARELE CATEGORII DE PROCESAT:")
    for cat in stats['unprocessed_categories'][:5]:
        print(f"   • {cat['name']}")
        print(f"     {cat['url']}")

def create_processing_queue(stats):
    """Creează un fișier cu coada de procesare"""
    queue_file = "processing_queue.txt"
    try:
        with open(queue_file, 'w', encoding='utf-8') as f:
            f.write("# Coada de procesare categorii BikeStylish\n")
            f.write(f"# Generat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total de procesat: {stats['unprocessed_count']}\n\n")
            
            for i, cat in enumerate(stats['unprocessed_categories'], 1):
                f.write(f"{i:3d}. {cat['id']}\n")
                f.write(f"     Nume: {cat['name']}\n")
                f.write(f"     URL:  {cat['url']}\n\n")
        
        print(f"\n💾 Coada de procesare salvată în: {queue_file}")
        
    except Exception as e:
        print(f"Eroare la crearea cozii: {e}")

def main():
    json_file = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    print(f"📂 Analizez fișierul: {json_file}")
    
    data = load_categories(json_file)
    if not data:
        return
    
    stats = analyze_categories(data)
    if not stats:
        print("❌ Nu s-au putut analiza categoriile")
        return
    
    print_report(stats)
    create_processing_queue(stats)
    
    # Calculează timpul estimat
    avg_time_per_category = 5  # secunde pe categorie
    estimated_time = stats['unprocessed_count'] * avg_time_per_category
    hours = estimated_time // 3600
    minutes = (estimated_time % 3600) // 60
    
    print(f"\n⏰ TIMP ESTIMAT RĂMAS:")
    if hours > 0:
        print(f"   Aproximativ {hours}h {minutes}m pentru categoriile rămase")
    else:
        print(f"   Aproximativ {minutes}m pentru categoriile rămase")
    
    print(f"\n🚀 Pentru a continua procesarea, rulează:")
    print(f"   python auto_update_categories.py")

if __name__ == "__main__":
    main()
