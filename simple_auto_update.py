#!/usr/bin/env python3
"""
Script simplu pentru actualizarea automată a categoriilor BikeStylish.
Versiune simplificată fără emoji-uri pentru compatibilitate Windows.
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

def load_categories():
    """Încarcă categoriile din JSON"""
    try:
        with open('data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Eroare la incarcarea JSON: {e}")
        return None

def save_categories(data):
    """Salvează categoriile în JSON"""
    try:
        with open('data/categories_ai_enhanced.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Eroare la salvarea JSON: {e}")
        return False

def extract_page_data(url):
    """Extrage datele din pagina de categorie"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrage numărul de produse
        product_count = 0
        products = soup.find_all(['div', 'article'], class_=re.compile(r'product|item'))
        product_count = len(products)
        
        if product_count == 0:
            # Încearcă alte selectors
            products = soup.find_all('a', href=re.compile(r'/produs/'))
            product_count = len(products)
        
        # Extrage prețurile
        prices = []
        price_elements = soup.find_all(text=re.compile(r'\d+[\.,]\d*\s*(lei|ron)', re.I))
        for price_text in price_elements[:20]:  # Limitează la 20 prețuri
            price_match = re.search(r'(\d+(?:[\.,]\d+)?)', price_text)
            if price_match:
                try:
                    price = float(price_match.group(1).replace(',', '.'))
                    if 10 <= price <= 10000:  # Prețuri rezonabile
                        prices.append(price)
                except:
                    continue
        
        # Extrage mărcile
        brands = set()
        brand_elements = soup.find_all(text=re.compile(r'\b[A-Z][A-Z\-]+\b'))
        for brand_text in brand_elements[:50]:
            brand_match = re.search(r'\b([A-Z][A-Z\-]{2,15})\b', brand_text)
            if brand_match:
                brand = brand_match.group(1)
                if len(brand) >= 3 and brand not in ['HTML', 'CSS', 'HTTP', 'WWW']:
                    brands.add(brand)
        
        # Calculează statistici prețuri
        price_range = {}
        if prices:
            price_range = {
                "min": min(prices),
                "max": max(prices),
                "avg": sum(prices) / len(prices)
            }
        
        return {
            "product_count": product_count,
            "price_range": price_range,
            "brands": list(brands)[:10],  # Limitează la 10 mărci
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Eroare la extragerea datelor din {url}: {e}")
        return None

def update_category(category_id, category_data):
    """Actualizează o categorie cu date reale"""
    if not category_data.get('url'):
        print(f"  - {category_id}: Nu are URL")
        return False
    
    print(f"  - Procesez: {category_id}")
    
    real_data = extract_page_data(category_data['url'])
    if not real_data:
        print(f"    EROARE: Nu s-au putut extrage date")
        return False
    
    # Actualizează categoria
    category_data['real_data'] = real_data
    
    print(f"    OK: {real_data['product_count']} produse, {len(real_data['brands'])} marci")
    return True

def main():
    print("=" * 60)
    print("ACTUALIZARE AUTOMATA CATEGORII BIKESTYLISH")
    print("=" * 60)
    print(f"Inceput: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Încarcă datele
    data = load_categories()
    if not data:
        print("EROARE: Nu s-a putut incarca JSON-ul")
        return
    
    categories = data.get('categories', {})
    total_categories = len(categories)
    processed_count = 0
    
    print(f"Total categorii: {total_categories}")
    
    # Identifică categoriile neprocesate
    unprocessed = []
    for cat_id, cat_data in categories.items():
        if not cat_data.get('real_data') or not cat_data['real_data'].get('product_count'):
            unprocessed.append(cat_id)
        else:
            processed_count += 1
    
    print(f"Deja procesate: {processed_count}")
    print(f"De procesat: {len(unprocessed)}")
    
    if not unprocessed:
        print("Toate categoriile sunt deja procesate!")
        return
    
    print("\nIncep procesarea...")
    
    # Procesează categoriile
    success_count = 0
    for i, category_id in enumerate(unprocessed, 1):
        print(f"\n[{i}/{len(unprocessed)}] Procesez categoria: {category_id}")
        
        if update_category(category_id, categories[category_id]):
            success_count += 1
            
            # Salvează progresul la fiecare 3 categorii
            if i % 3 == 0:
                if save_categories(data):
                    print(f"  PROGRES SALVAT: {i} categorii procesate")
                else:
                    print(f"  EROARE la salvarea progresului")
        
        # Pauză între cereri
        if i < len(unprocessed):
            time.sleep(2)
    
    # Salvare finală
    if save_categories(data):
        print(f"\nFINALIZAT: {success_count}/{len(unprocessed)} categorii actualizate cu succes")
    else:
        print("\nERORE la salvarea finala!")

if __name__ == "__main__":
    main()
