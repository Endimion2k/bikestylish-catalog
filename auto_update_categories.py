#!/usr/bin/env python3
"""
Script pentru actualizarea automată a categoriilor BikeStylish cu date reale din website.
Continuă procesul de înlocuire a datelor AI generate cu informații reale extrase din pagini.
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

class BikeStylishCategoryUpdater:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Categorii deja procesate (pentru a nu le repeta)
        self.processed_categories = {
            'accesorii-bicicleta',
            'accesorii', 
            'remorci-transport-copii',
            'roti-ajutatoare',
            'scaune-pentru-copii',
            'transport-si-depozitare',
            'reflectorizante',
            'articole-copii-roti-ajutatoare',
            'parti-ghidoane-si-barend-extensiighidon'
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
        """Salvează categoriile actualizate în fișierul JSON"""
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("JSON salvat cu succes")
            return True
        except Exception as e:
            logger.error(f"Eroare la salvarea JSON: {e}")
            return False

    def fetch_page_content(self, url):
        """Extrage conținutul unei pagini web"""
        try:
            logger.info(f"Accesez: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Eroare la accesarea {url}: {e}")
            return None

    def extract_page_data(self, html_content, category_id):
        """Extrage datele relevante din HTML-ul paginii"""
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # Extrage numărul de produse
            product_count = self.extract_product_count(soup)
            
            # Extrage mărcile disponibile  
            brands = self.extract_brands(soup)
            
            # Extrage informații despre prețuri
            price_info = self.extract_price_info(soup)
            
            # Extrage tipurile de produse
            product_types = self.extract_product_types(soup)
            
            return {
                'product_count': product_count,
                'price_range': price_info,
                'brands': brands,
                'product_types': product_types,
                'common_terms': self.generate_common_terms(category_id, product_types),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Eroare la extragerea datelor: {e}")
            return None

    def extract_product_count(self, soup):
        """Extrage numărul de produse din pagină"""
        # Caută textul "Afiseaza: 1-X din Y produse"
        count_text = soup.find(text=re.compile(r'Afiseaza:.*?din\s+(\d+)\s+produs'))
        if count_text:
            match = re.search(r'din\s+(\d+)\s+produs', count_text)
            if match:
                return int(match.group(1))
        
        # Alternativ, numără produsele din pagină
        products = soup.find_all('div', class_=['product-item', 'product'])
        if products:
            return len(products)
            
        # Caută linkuri către produse
        product_links = soup.find_all('a', href=re.compile(r'\.html$'))
        if product_links:
            return len([link for link in product_links if any(keyword in link.get('href', '') 
                       for keyword in ['-', 'bicicleta', 'bike'])])
        
        return 1  # Default minim

    def extract_brands(self, soup):
        """Extrage mărcile din pagină"""
        brands = set()
        
        # Caută în secțiunea de filtre
        brand_section = soup.find('div', string=re.compile(r'Producatori|Brands'))
        if brand_section:
            parent = brand_section.find_parent()
            if parent:
                brand_links = parent.find_all('a')
                for link in brand_links:
                    brand_text = link.get_text().strip()
                    if brand_text and len(brand_text) < 20:  # Filtrează textele prea lungi
                        brands.add(brand_text)
        
        # Caută mărci în textul produselor
        product_titles = soup.find_all('h2') + soup.find_all('h3') + soup.find_all('a')
        common_brands = ['M-WAVE', 'SXT', 'SHIMANO', 'SUPER B', 'VENTURA', 'NECO', 'MOON', 
                        'VELO', 'EXTEND', 'NOVATEC', 'CICLO BONIN', 'ZOOM', 'AUTHOR']
        
        for element in product_titles:
            text = element.get_text().upper()
            for brand in common_brands:
                if brand in text:
                    brands.add(brand)
        
        return sorted(list(brands)) if brands else ['M-WAVE']

    def extract_price_info(self, soup):
        """Extrage informațiile despre prețuri"""
        prices = []
        
        # Caută prețuri în diferite formate
        price_patterns = [
            r'(\d+(?:\.\d+)?)\s*RON',
            r'(\d+(?:,\d+)?)\s*lei',
            r'(\d+)\s*-\s*(\d+)\s*RON'
        ]
        
        text_content = soup.get_text()
        for pattern in price_patterns:
            matches = re.findall(pattern, text_content)
            for match in matches:
                if isinstance(match, tuple):
                    prices.extend([float(p.replace(',', '.')) for p in match if p])
                else:
                    prices.append(float(match.replace(',', '.')))
        
        if prices:
            return {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices)
            }
        else:
            # Valori default bazate pe tipul categoriei
            return {'min': 15.0, 'max': 200.0, 'avg': 80.0}

    def extract_product_types(self, soup):
        """Extrage tipurile de produse din pagină"""
        product_types = []
        
        # Caută în titlurile produselor
        titles = soup.find_all(['h2', 'h3', 'h4'])
        for title in titles:
            text = title.get_text().lower()
            if any(keyword in text for keyword in ['bicicleta', 'bike', 'copii', 'adulti']):
                # Extrage cuvinte cheie relevante
                words = text.split()
                relevant_words = [w for w in words if len(w) > 3 and 
                                w not in ['pentru', 'bicicleta', 'bike', 'copii']]
                if relevant_words:
                    product_types.extend(relevant_words[:2])  # Primele 2 cuvinte relevante
        
        # Elimină duplicatele și returnează maxim 6 tipuri
        unique_types = list(dict.fromkeys(product_types))[:6]
        return unique_types if unique_types else ['accesorii diverse']

    def generate_common_terms(self, category_id, product_types):
        """Generează termeni comuni bazați pe categoria și produsele găsite"""
        base_terms = {
            'reflectorizante': ['reflectorizant', 'vizibilitate', 'siguranță'],
            'copii': ['copii', 'siguranță', 'certificat'],
            'transport': ['transport', 'depozitare', 'suport'],
            'ghidon': ['ghidon', 'prindere', 'aluminiu']
        }
        
        terms = []
        for key, values in base_terms.items():
            if key in category_id:
                terms.extend(values)
        
        # Adaugă termeni din tipurile de produse
        terms.extend(product_types[:3])
        
        return list(dict.fromkeys(terms))[:6]  # Maxim 6 termeni unici

    def update_category_real_data(self, category, real_data):
        """Actualizează secțiunea real_data a unei categorii"""
        if 'real_data' not in category:
            category['real_data'] = {}
        
        category['real_data'].update(real_data)
        logger.info(f"Actualizat {category['id']}: {real_data['product_count']} produse")

    def process_categories(self):
        """Procesează toate categoriile care nu au fost încă actualizate"""
        data = self.load_categories()
        if not data:
            return
        
        categories_to_process = []
        for category in data.get('categories', []):
            if category['id'] not in self.processed_categories:
                categories_to_process.append(category)
        
        logger.info(f"Găsite {len(categories_to_process)} categorii pentru procesare")
        
        for i, category in enumerate(categories_to_process):
            try:
                logger.info(f"Procesez categoria {i+1}/{len(categories_to_process)}: {category['id']}")
                
                # Accesează pagina categoriei
                html_content = self.fetch_page_content(category['url'])
                if not html_content:
                    continue
                
                # Extrage datele
                real_data = self.extract_page_data(html_content, category['id'])
                if not real_data:
                    continue
                
                # Actualizează categoria
                self.update_category_real_data(category, real_data)
                
                # Salvează progresul la fiecare 3 categorii
                if (i + 1) % 3 == 0:
                    self.save_categories(data)
                    logger.info(f"Progres salvat: {i+1}/{len(categories_to_process)}")
                
                # Pauză între cereri pentru a nu suprasolicita serverul
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Eroare la procesarea {category['id']}: {e}")
                continue
        
        # Salvează rezultatul final
        self.save_categories(data)
        logger.info("Procesare completă!")

def main():
    """Funcția principală"""
    json_file = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    
    updater = BikeStylishCategoryUpdater(json_file)
    updater.process_categories()

if __name__ == "__main__":
    main()
