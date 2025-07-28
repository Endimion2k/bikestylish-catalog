#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script avansat pentru extragerea completă a conținutului din paginile de categorii BikeStylish.
Extrage: FAQ-uri, ghiduri alegere, tehnologii, tips montaj, informații tehnice, etc.
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedContentExtractor:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Categorii deja procesate manual
        self.processed_categories = {
            'accesorii-bicicleta', 'accesorii', 'remorci-transport-copii',
            'roti-ajutatoare', 'scaune-pentru-copii', 'transport-si-depozitare',
            'reflectorizante', 'articole-copii-roti-ajutatoare',
            'parti-ghidoane-si-barend-extensiighidon', 'cricuri-de-mijloc',
            'cosuri-pentru-biciclete'
        }

    def load_categories(self):
        """Încarcă categoriile din fișierul JSON"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Eroare la încărcarea JSON: {e}")
            return None

    def save_categories(self, data):
        """Salvează categoriile actualizate"""
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("JSON salvat cu succes")
            return True
        except Exception as e:
            logger.error(f"Eroare la salvarea JSON: {e}")
            return False

    def fetch_page_content(self, url):
        """Extrage conținutul complet al paginii"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Eroare la accesarea {url}: {e}")
            return None

    def extract_faq_content(self, soup):
        """Extrage FAQ-uri din pagină"""
        faqs = []
        
        # Caută secțiuni FAQ
        faq_sections = soup.find_all(['section', 'div'], class_=re.compile(r'faq|questions|intrebari', re.I))
        
        for section in faq_sections:
            # Caută perechi întrebare-răspuns
            questions = section.find_all(['h2', 'h3', 'h4', 'dt'], string=re.compile(r'\?|Ce|Cum|Care|De ce|Când'))
            
            for q in questions:
                question_text = q.get_text().strip()
                if len(question_text) > 10:  # Filtrează întrebările prea scurte
                    # Găsește răspunsul (următorul element sau următorul paragraf)
                    answer_element = q.find_next_sibling(['p', 'div', 'dd', 'span'])
                    if answer_element:
                        answer_text = answer_element.get_text().strip()
                        if len(answer_text) > 20:  # Filtrează răspunsurile prea scurte
                            faqs.append({
                                "question": question_text,
                                "answer": answer_text[:500] + "..." if len(answer_text) > 500 else answer_text
                            })
        
        # Caută și în accordeon/collapse structures
        accordions = soup.find_all(['div', 'section'], class_=re.compile(r'accordion|collapse|toggle', re.I))
        for accordion in accordions:
            headers = accordion.find_all(['button', 'h3', 'h4'], string=re.compile(r'\?|Ce|Cum|Care'))
            for header in headers:
                content_div = header.find_next_sibling(['div', 'p'])
                if content_div:
                    faqs.append({
                        "question": header.get_text().strip(),
                        "answer": content_div.get_text().strip()[:500]
                    })
        
        return faqs[:10]  # Limitează la maxim 10 FAQ-uri

    def extract_buying_guide(self, soup):
        """Extrage ghidul de alegere"""
        guide_content = []
        
        # Caută secțiuni de ghid
        guide_sections = soup.find_all(['section', 'div'], string=re.compile(r'ghid|alegere|cum să alegi|guide', re.I))
        
        for section in guide_sections:
            parent = section.find_parent()
            if parent:
                # Extrage pașii sau punctele importante
                steps = parent.find_all(['li', 'p', 'div'], string=re.compile(r'1\.|2\.|pas|step|important', re.I))
                for step in steps[:5]:  # Maxim 5 pași
                    text = step.get_text().strip()
                    if len(text) > 30:
                        guide_content.append(text[:300])
        
        # Caută și în conținutul principal
        main_content = soup.find(['main', 'article', 'div'], class_=re.compile(r'content|main', re.I))
        if main_content:
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text()
                if any(keyword in text.lower() for keyword in ['alege', 'important', 'trebuie', 'recomand']):
                    guide_content.append(text.strip()[:300])
        
        return guide_content[:8]  # Maxim 8 sfaturi

    def extract_technical_specs(self, soup):
        """Extrage specificații tehnice"""
        specs = {}
        
        # Caută tabele cu specificații
        spec_tables = soup.find_all('table')
        for table in spec_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if key and value and len(key) < 50:
                        specs[key] = value
        
        # Caută liste cu specificații
        spec_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'spec|features|caracterstici', re.I))
        for spec_list in spec_lists:
            items = spec_list.find_all('li')
            for item in items:
                text = item.get_text().strip()
                if ':' in text:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        specs[parts[0].strip()] = parts[1].strip()
        
        return dict(list(specs.items())[:10])  # Maxim 10 specificații

    def extract_installation_tips(self, soup):
        """Extrage tips de montaj/instalare"""
        tips = []
        
        # Caută secțiuni de instalare
        install_sections = soup.find_all(['section', 'div'], string=re.compile(r'montaj|instalare|install|tips', re.I))
        
        for section in install_sections:
            parent = section.find_parent()
            if parent:
                steps = parent.find_all(['li', 'p'], string=re.compile(r'pas|step|atenție|important', re.I))
                for step in steps:
                    text = step.get_text().strip()
                    if len(text) > 20:
                        tips.append(text[:250])
        
        # Caută și warnings/atenționări
        warnings = soup.find_all(['div', 'p'], class_=re.compile(r'warning|alert|atentie', re.I))
        for warning in warnings:
            text = warning.get_text().strip()
            if len(text) > 20:
                tips.append(f"⚠️ {text[:200]}")
        
        return tips[:6]  # Maxim 6 tips

    def extract_technologies(self, soup):
        """Extrage informații despre tehnologii"""
        technologies = []
        
        # Caută mențiuni de tehnologii
        tech_keywords = ['LED', 'USB', 'Bluetooth', 'GPS', 'ANT+', 'Li-ion', 'carbon', 'aluminiu', 
                        'titanium', 'ceramic', 'hydraulic', 'mechanical', 'electronic']
        
        all_text = soup.get_text()
        found_techs = []
        
        for tech in tech_keywords:
            if tech.lower() in all_text.lower():
                # Găsește contextul tehnologiei
                sentences = re.split(r'[.!?]', all_text)
                for sentence in sentences:
                    if tech.lower() in sentence.lower() and len(sentence.strip()) > 20:
                        found_techs.append(f"{tech}: {sentence.strip()[:200]}")
                        break
        
        return found_techs[:5]  # Maxim 5 tehnologii

    def extract_product_info(self, soup):
        """Extrage informații generale despre produse"""
        info = {
            'product_count': 0,
            'price_range': '',
            'top_brands': [],
            'categories': []
        }
        
        # Numărul de produse
        count_text = soup.find(text=re.compile(r'din\s+(\d+)\s+produs'))
        if count_text:
            match = re.search(r'din\s+(\d+)\s+produs', count_text)
            if match:
                info['product_count'] = int(match.group(1))
        
        # Găsește prețuri
        prices = soup.find_all(text=re.compile(r'\d+[\.,]\d*\s*(?:RON|lei)'))
        if prices:
            price_values = []
            for price in prices:
                match = re.search(r'(\d+)[\.,](\d*)', price)
                if match:
                    price_values.append(int(match.group(1)))
            
            if price_values:
                info['price_range'] = f"{min(price_values)}-{max(price_values)} RON"
        
        # Găsește mărci
        brands = set()
        common_brands = ['M-WAVE', 'SXT', 'SHIMANO', 'SUPER B', 'VENTURA', 'NECO', 'MOON']
        for brand in common_brands:
            if brand in soup.get_text().upper():
                brands.add(brand)
        info['top_brands'] = list(brands)[:5]
        
        return info

    def process_category(self, category):
        """Procesează o categorie completă"""
        category_id = category.get('id', 'unknown')
        url = category.get('url', '')
        
        if not url:
            logger.warning(f"URL lipsă pentru categoria {category_id}")
            return False
        
        logger.info(f"Procesez categoria: {category_id}")
        logger.info(f"Accesez: {url}")
        
        # Extrage conținutul paginii
        soup = self.fetch_page_content(url)
        if not soup:
            return False
        
        # Extrage toate tipurile de conținut
        extracted_content = {
            'web_extracted_faqs': self.extract_faq_content(soup),
            'buying_guide': self.extract_buying_guide(soup),
            'technical_specifications': self.extract_technical_specs(soup),
            'installation_tips': self.extract_installation_tips(soup),
            'technologies': self.extract_technologies(soup),
            'product_info': self.extract_product_info(soup),
            'extraction_date': datetime.now().isoformat(),
            'source_url': url
        }
        
        # Actualizează categoria cu conținutul extras
        if 'content_structure' not in category:
            category['content_structure'] = {}
        
        # Adaugă conținutul nou extras
        category['content_structure']['web_extracted_content'] = extracted_content
        
        # Actualizează și datele de bază
        product_info = extracted_content['product_info']
        if product_info['product_count'] > 0:
            if 'schema_markup' in category['content_structure']:
                if 'collection_page' in category['content_structure']['schema_markup']:
                    category['content_structure']['schema_markup']['collection_page']['numberOfItems'] = product_info['product_count']
        
        logger.info(f"✅ Extras conținut complet pentru {category_id}:")
        logger.info(f"   - FAQ-uri: {len(extracted_content['web_extracted_faqs'])}")
        logger.info(f"   - Ghid alegere: {len(extracted_content['buying_guide'])} sfaturi")
        logger.info(f"   - Specificații: {len(extracted_content['technical_specifications'])} items")
        logger.info(f"   - Tips instalare: {len(extracted_content['installation_tips'])}")
        logger.info(f"   - Tehnologii: {len(extracted_content['technologies'])}")
        logger.info(f"   - Produse găsite: {product_info['product_count']}")
        
        return True

    def run_extraction(self):
        """Rulează extragerea pentru toate categoriile"""
        data = self.load_categories()
        if not data:
            return
        
        categories = data.get('categories', [])
        if not categories:
            logger.error("Nu s-au găsit categorii în JSON")
            return
        
        # Filtrează categoriile care nu au fost procesate
        categories_to_process = [
            cat for cat in categories 
            if cat.get('id') not in self.processed_categories
        ]
        
        logger.info(f"Găsite {len(categories_to_process)} categorii pentru procesare avansată")
        
        processed_count = 0
        for i, category in enumerate(categories_to_process, 1):
            try:
                logger.info(f"\n=== Procesez categoria {i}/{len(categories_to_process)} ===")
                
                if self.process_category(category):
                    processed_count += 1
                    
                    # Salvează progresul la fiecare 5 categorii
                    if processed_count % 5 == 0:
                        self.save_categories(data)
                        logger.info(f"✅ Progres salvat: {processed_count}/{len(categories_to_process)}")
                
                # Pauză între cereri pentru a nu supraîncărca serverul
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Eroare la procesarea categoriei {category.get('id', 'unknown')}: {e}")
                continue
        
        # Salvează versiunea finală
        self.save_categories(data)
        logger.info(f"\n🎉 FINALIZAT! Procesate {processed_count} categorii cu conținut complet!")

if __name__ == "__main__":
    extractor = AdvancedContentExtractor(
        r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    )
    extractor.run_extraction()
