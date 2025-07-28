#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizator specific pentru detectarea structurii dropdown FAQ de pe BikeStylish
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def analyze_page_structure_for_faqs():
    """Analizează structura paginii pentru FAQ-uri dropdown"""
    url = "https://www.bikestylish.ro/ghidoline"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 ANALIZA DETALIATĂ A STRUCTURII FAQ DROPDOWN\n")
        
        # 1. Caută toate elementele care conțin cuvinte cheie FAQ
        faq_keywords = ['intreb', 'raspuns', 'frecvent', 'question', 'faq', 'ghid', 'cum', 'ce este']
        
        print("📋 1. ELEMENTE CU CUVINTE CHEIE FAQ:")
        elements_with_faq_text = []
        
        for keyword in faq_keywords:
            elements = soup.find_all(string=re.compile(keyword, re.I))
            for element in elements:
                parent = element.parent
                if parent and len(element.strip()) > 10:
                    elements_with_faq_text.append({
                        'text': element.strip()[:100],
                        'parent_tag': parent.name,
                        'parent_classes': parent.get('class', []),
                        'parent_id': parent.get('id', ''),
                        'keyword_found': keyword
                    })
        
        for i, elem in enumerate(elements_with_faq_text[:5], 1):
            print(f"   {i}. Keyword '{elem['keyword_found']}' în {elem['parent_tag']}")
            print(f"      Text: {elem['text']}")
            print(f"      Clase: {elem['parent_classes']}")
            if elem['parent_id']:
                print(f"      ID: {elem['parent_id']}")
            print()
        
        # 2. Caută toate elementele cu atribute specifice dropdown
        print("🔽 2. ELEMENTE CU ATRIBUTE DROPDOWN:")
        dropdown_attributes = [
            'data-toggle', 'data-bs-toggle', 'data-target', 'data-bs-target',
            'aria-expanded', 'aria-controls', 'collapse', 'accordion'
        ]
        
        dropdown_elements = []
        for attr in dropdown_attributes:
            elements = soup.find_all(attrs={attr: True})
            for elem in elements:
                dropdown_elements.append({
                    'tag': elem.name,
                    'text': elem.get_text().strip()[:80],
                    'attribute': attr,
                    'attribute_value': elem.get(attr),
                    'classes': elem.get('class', []),
                    'id': elem.get('id', '')
                })
        
        for i, elem in enumerate(dropdown_elements[:10], 1):
            print(f"   {i}. <{elem['tag']}> {elem['attribute']}=\"{elem['attribute_value']}\"")
            print(f"      Text: {elem['text']}")
            print(f"      Clase: {elem['classes']}")
            if elem['id']:
                print(f"      ID: {elem['id']}")
            print()
        
        # 3. Caută clase CSS care sugerează FAQ/accordion
        print("🎨 3. CLASE CSS RELEVANTE:")
        css_patterns = [
            'faq', 'accordion', 'collapse', 'dropdown', 'toggle',
            'expand', 'question', 'answer', 'panel', 'card'
        ]
        
        relevant_classes = set()
        all_elements = soup.find_all(class_=True)
        
        for element in all_elements:
            element_classes = element.get('class', [])
            for class_name in element_classes:
                for pattern in css_patterns:
                    if pattern.lower() in class_name.lower():
                        relevant_classes.add(class_name)
        
        for i, class_name in enumerate(sorted(relevant_classes)[:15], 1):
            elements_with_class = soup.find_all(class_=re.compile(class_name, re.I))
            print(f"   {i}. .{class_name} (găsită în {len(elements_with_class)} elemente)")
        
        print()
        
        # 4. Caută structuri taburi care ar putea conține FAQ
        print("📑 4. STRUCTURI TABURI CU POSIBILE FAQ:")
        tab_elements = soup.find_all(['a', 'button'], attrs={'data-toggle': True})
        tab_elements.extend(soup.find_all(['a', 'button'], attrs={'data-bs-toggle': True}))
        
        for i, tab in enumerate(tab_elements[:8], 1):
            tab_text = tab.get_text().strip()
            target = tab.get('data-target', tab.get('data-bs-target', tab.get('href', '')))
            
            print(f"   {i}. Tab: \"{tab_text}\"")
            print(f"      Target: {target}")
            
            # Încearcă să găsească conținutul target
            if target.startswith('#'):
                target_element = soup.find(id=target[1:])
                if target_element:
                    target_text = target_element.get_text().strip()
                    print(f"      Conținut target: {target_text[:100]}...")
                    
                    # Verifică dacă conținutul pare a fi FAQ
                    if any(word in target_text.lower() for word in ['?', 'cum', 'ce este', 'ghid']):
                        print(f"      ✅ POSIBIL FAQ CONTENT!")
            print()
        
        # 5. Caută JavaScript inline care gestionează dropdown-uri
        print("⚡ 5. SCRIPT-URI JAVASCRIPT RELEVANTE:")
        scripts = soup.find_all('script')
        js_functions = []
        
        for script in scripts:
            if script.string:
                content = script.string
                # Caută funcții relevante
                if any(word in content.lower() for word in ['collapse', 'toggle', 'dropdown', 'accordion', 'tab']):
                    # Extrage numele funcțiilor
                    function_matches = re.findall(r'function\s+(\w+)|(\w+)\s*:\s*function', content)
                    for match in function_matches:
                        func_name = match[0] or match[1]
                        if func_name:
                            js_functions.append(func_name)
                    
                    # Caută event listeners
                    event_matches = re.findall(r'addEventListener\s*\(\s*[\'"](\w+)[\'"]', content)
                    js_functions.extend(event_matches)
        
        unique_js_functions = list(set(js_functions))
        for i, func in enumerate(unique_js_functions[:10], 1):
            print(f"   {i}. Funcție JS: {func}")
        
        print()
        
        # 6. Salvează structura detaliată pentru debugging
        analysis_data = {
            'faq_elements': elements_with_faq_text[:10],
            'dropdown_elements': dropdown_elements[:15],
            'relevant_css_classes': list(relevant_classes),
            'tab_structures': [
                {
                    'text': tab.get_text().strip(),
                    'target': tab.get('data-target', tab.get('data-bs-target', tab.get('href', ''))),
                    'tag': tab.name,
                    'classes': tab.get('class', [])
                }
                for tab in tab_elements[:10]
            ],
            'js_functions': unique_js_functions[:15]
        }
        
        with open('faq_structure_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        print("💾 Analiza salvată în 'faq_structure_analysis.json'")
        return analysis_data
        
    except Exception as e:
        print(f"❌ Eroare: {e}")
        return None

if __name__ == "__main__":
    analyze_page_structure_for_faqs()
