#!/usr/bin/env python3
"""
Script test pentru extragerea conținutului unei singure categorii
"""

import json
import requests
from bs4 import BeautifulSoup
import re

def extract_detailed_content():
    """Test pentru o singură categorie"""
    
    # Încarcă JSON-ul
    json_path = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Găsește o categorie de test (care nu a fost procesată manual)
    categories = data.get('categories', [])
    test_category = None
    
    for cat in categories:
        if cat.get('id') == 'ghidoline':  # Categorie test
            test_category = cat
            break
    
    if not test_category:
        print("❌ Nu s-a găsit categoria de test")
        return
    
    url = test_category.get('url', '')
    print(f"🔍 Testez categoria: {test_category.get('id')}")
    print(f"📍 URL: {url}")
    
    # Fetch pagina
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Eroare HTTP: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    print(f"✅ Pagina încărcată cu succes")
    
    # Extrage conținut
    extracted_content = {
        'page_title': soup.title.get_text() if soup.title else 'N/A',
        'h1_headings': [h1.get_text().strip() for h1 in soup.find_all('h1')],
        'h2_headings': [h2.get_text().strip() for h2 in soup.find_all('h2')],
        'paragraphs': [p.get_text().strip()[:200] for p in soup.find_all('p') if len(p.get_text().strip()) > 50][:5],
        'product_count': 0,
        'found_faqs': [],
        'found_guides': []
    }
    
    # Caută numărul de produse
    count_text = soup.find(text=re.compile(r'din\s+(\d+)\s+produs'))
    if count_text:
        match = re.search(r'din\s+(\d+)\s+produs', count_text)
        if match:
            extracted_content['product_count'] = int(match.group(1))
    
    # Caută FAQ-uri
    all_text = soup.get_text()
    faq_indicators = ['?', 'Ce ', 'Cum ', 'Care ', 'De ce ', 'Când ']
    sentences = re.split(r'[.!?]', all_text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(indicator in sentence for indicator in faq_indicators) and len(sentence) > 20:
            extracted_content['found_faqs'].append(sentence[:150])
            if len(extracted_content['found_faqs']) >= 5:
                break
    
    # Caută ghiduri
    guide_keywords = ['alege', 'important', 'trebuie', 'recomandat', 'sfat']
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in guide_keywords) and len(sentence) > 30:
            extracted_content['found_guides'].append(sentence[:200])
            if len(extracted_content['found_guides']) >= 3:
                break
    
    # Afișează rezultatele
    print(f"\n📊 REZULTATE EXTRAGERE:")
    print(f"🏷️  Titlu pagină: {extracted_content['page_title']}")
    print(f"📝 H1 headings: {len(extracted_content['h1_headings'])}")
    print(f"📝 H2 headings: {len(extracted_content['h2_headings'])}")
    print(f"📝 Paragrafe: {len(extracted_content['paragraphs'])}")
    print(f"🛍️  Produse găsite: {extracted_content['product_count']}")
    print(f"❓ FAQ-uri găsite: {len(extracted_content['found_faqs'])}")
    print(f"📖 Ghiduri găsite: {len(extracted_content['found_guides'])}")
    
    print(f"\n📋 EXEMPLE FAQ-URI:")
    for i, faq in enumerate(extracted_content['found_faqs'][:3], 1):
        print(f"   {i}. {faq}")
    
    print(f"\n📖 EXEMPLE GHIDURI:")
    for i, guide in enumerate(extracted_content['found_guides'][:2], 1):
        print(f"   {i}. {guide}")
    
    # Actualizează categoria în JSON
    if 'content_structure' not in test_category:
        test_category['content_structure'] = {}
    
    test_category['content_structure']['web_extracted_detailed'] = extracted_content
    
    # Salvează JSON-ul actualizat
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Categoria actualizată cu conținut detaliat în JSON!")

if __name__ == "__main__":
    extract_detailed_content()
