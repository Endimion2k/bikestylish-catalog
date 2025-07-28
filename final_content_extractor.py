#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final pentru extragerea conținutului complet din BikeStylish
Include simularea interacțiunii cu taburi JavaScript prin cereri HTTP
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalContentExtractor:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'  # Pentru cereri AJAX
        })
        
        # Categorii procesate manual
        self.processed_categories = {
            'accesorii-bicicleta', 'accesorii', 'remorci-transport-copii',
            'roti-ajutatoare', 'scaune-pentru-copii', 'transport-si-depozitare',
            'reflectorizante', 'articole-copii-roti-ajutatoare',
            'parti-ghidoane-si-barend-extensiighidon', 'cricuri-de-mijloc',
            'cosuri-pentru-biciclete'
        }

    def load_categories(self):
        """Încarcă categoriile din JSON"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Eroare la încărcarea JSON: {e}")
            return None

    def save_categories(self, data):
        """Salvează categoriile"""
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Eroare la salvarea JSON: {e}")
            return False

    def extract_complete_content(self, url, category_id):
        """Extrage conținut complet din pagină + taburi"""
        try:
            # Primul request pentru pagina principală
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            main_soup = BeautifulSoup(response.content, 'html.parser')
            
            extracted_data = {
                'extraction_timestamp': datetime.now().isoformat(),
                'source_url': url,
                'main_content': self._extract_page_content(main_soup),
                'tab_content': {},
                'comprehensive_data': {}
            }
            
            # Caută și încearcă să acceseze conținutul din taburi
            tab_content = self._try_extract_tab_content(url, main_soup)
            extracted_data['tab_content'] = tab_content
            
            # Combină tot conținutul
            extracted_data['comprehensive_data'] = self._combine_all_content(
                extracted_data['main_content'], 
                tab_content
            )
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Eroare la extragerea pentru {category_id}: {e}")
            return None

    def _extract_page_content(self, soup):
        """Extrage conținutul principal al paginii"""
        content = {
            'title': soup.title.get_text().strip() if soup.title else '',
            'headings': {
                'h1': [h.get_text().strip() for h in soup.find_all('h1')],
                'h2': [h.get_text().strip() for h in soup.find_all('h2')],
                'h3': [h.get_text().strip() for h in soup.find_all('h3')]
            },
            'descriptions': [],
            'features_lists': [],
            'technical_specs': {},
            'faqs': [],
            'guides': [],
            'product_info': {
                'count': 0,
                'brands': [],
                'price_range': ''
            }
        }
        
        # Extrage descrieri din paragrafe
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 50:
                content['descriptions'].append(text[:400])
                if len(content['descriptions']) >= 10:
                    break
        
        # Extrage liste de caracteristici
        for ul in soup.find_all(['ul', 'ol']):
            items = []
            for li in ul.find_all('li'):
                item_text = li.get_text().strip()
                if len(item_text) > 10:
                    items.append(item_text)
            if len(items) > 2:
                content['features_lists'].append(items[:10])
        
        # Caută specificații în tabele
        for table in soup.find_all('table'):
            for tr in table.find_all('tr'):
                cells = tr.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if key and value and len(key) < 50:
                        content['technical_specs'][key] = value
        
        # Extrage FAQ-uri potențiale
        page_text = soup.get_text()
        questions = re.findall(r'[A-ZÀ-ÿ][^.!?]*\?', page_text)
        for q in questions:
            if any(word in q.lower() for word in ['ce', 'cum', 'care', 'de ce', 'când']):
                if 20 <= len(q) <= 150:
                    content['faqs'].append(q.strip())
                    if len(content['faqs']) >= 8:
                        break
        
        # Extrage informații despre produse
        count_match = re.search(r'din\s+(\d+)\s+produs', page_text, re.IGNORECASE)
        if count_match:
            content['product_info']['count'] = int(count_match.group(1))
        
        # Găsește mărci
        brands = ['M-WAVE', 'SXT', 'SHIMANO', 'SUPER B', 'VENTURA', 'NECO', 'AUTHOR', 'DEDA']
        for brand in brands:
            if brand in page_text.upper():
                content['product_info']['brands'].append(brand)
        
        return content

    def _try_extract_tab_content(self, base_url, soup):
        """Încearcă să extragă conținut din taburi prin diverse metode"""
        tab_content = {}
        
        # Metodă 1: Caută linkuri către alte pagini/secțiuni
        links = soup.find_all('a', href=True)
        category_related_links = []
        
        base_path = urlparse(base_url).path.rstrip('/')
        
        for link in links:
            href = link.get('href', '')
            link_text = link.get_text().strip()
            
            # Caută linkuri care par să fie taburi/secțiuni
            if (href.startswith(base_path) and href != base_path and 
                any(keyword in link_text.lower() for keyword in 
                    ['descriere', 'specificații', 'ghid', 'instalare', 'caracteristici', 'detalii'])):
                category_related_links.append({
                    'url': urljoin(base_url, href),
                    'text': link_text,
                    'href': href
                })
        
        # Încearcă să acceseze linkurile găsite
        for link_info in category_related_links[:5]:
            try:
                logger.info(f"🔗 Încerc să accesez: {link_info['text']} -> {link_info['url']}")
                
                response = self.session.get(link_info['url'], timeout=20)
                if response.status_code == 200:
                    link_soup = BeautifulSoup(response.content, 'html.parser')
                    link_content = self._extract_page_content(link_soup)
                    tab_content[link_info['text']] = link_content
                    logger.info(f"✅ Conținut extras din: {link_info['text']}")
                    
                time.sleep(1)  # Pauză între cereri
                
            except Exception as e:
                logger.warning(f"⚠️ Eroare la accesarea {link_info['url']}: {e}")
        
        # Metodă 2: Caută secțiuni cu ID-uri specifice în aceeași pagină
        sections_with_ids = soup.find_all(['div', 'section'], id=True)
        for section in sections_with_ids:
            section_id = section.get('id', '')
            if any(keyword in section_id.lower() for keyword in 
                   ['tab', 'content', 'detail', 'spec', 'faq', 'guide']):
                section_content = self._extract_section_content(section)
                if section_content:
                    tab_content[f"section_{section_id}"] = section_content
        
        # Metodă 3: Caută conținut în elementele cu clase specifice
        content_divs = soup.find_all(['div', 'section'], class_=re.compile(r'content|detail|tab|panel', re.I))
        for i, div in enumerate(content_divs[:5]):
            div_content = self._extract_section_content(div)
            if div_content and div_content.get('descriptions'):
                tab_content[f"content_section_{i+1}"] = div_content
        
        return tab_content

    def _extract_section_content(self, section):
        """Extrage conținut dintr-o secțiune specifică"""
        content = {
            'descriptions': [],
            'lists': [],
            'specs': {},
            'headings': []
        }
        
        # Headings din secțiune
        for h in section.find_all(['h1', 'h2', 'h3', 'h4']):
            content['headings'].append(h.get_text().strip())
        
        # Paragrafe
        for p in section.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 30:
                content['descriptions'].append(text[:300])
        
        # Liste
        for ul in section.find_all(['ul', 'ol']):
            items = [li.get_text().strip() for li in ul.find_all('li')]
            if items:
                content['lists'].append(items)
        
        # Tabele pentru specificații
        for table in section.find_all('table'):
            for tr in table.find_all('tr'):
                cells = tr.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if key and value:
                        content['specs'][key] = value
        
        return content if any(content.values()) else None

    def _combine_all_content(self, main_content, tab_content):
        """Combină conținutul din toate sursele"""
        combined = {
            'total_descriptions': [],
            'all_features': [],
            'complete_specs': {},
            'comprehensive_faqs': [],
            'buying_guides': [],
            'installation_info': [],
            'brand_info': main_content['product_info']['brands'],
            'product_count': main_content['product_info']['count'],
            'all_headings': []
        }
        
        # Adaugă conținutul principal
        combined['total_descriptions'].extend(main_content['descriptions'])
        combined['all_features'].extend(main_content['features_lists'])
        combined['complete_specs'].update(main_content['technical_specs'])
        combined['comprehensive_faqs'].extend(main_content['faqs'])
        combined['all_headings'].extend(main_content['headings']['h1'])
        combined['all_headings'].extend(main_content['headings']['h2'])
        
        # Adaugă conținutul din taburi
        for tab_name, tab_data in tab_content.items():
            if isinstance(tab_data, dict):
                if 'descriptions' in tab_data:
                    combined['total_descriptions'].extend(tab_data['descriptions'])
                if 'lists' in tab_data:
                    combined['all_features'].extend(tab_data['lists'])
                if 'specs' in tab_data:
                    combined['complete_specs'].update(tab_data['specs'])
                if 'headings' in tab_data:
                    combined['all_headings'].extend(tab_data['headings'])
                
                # Analizează tipul de conținut bazat pe numele tabului
                if any(keyword in tab_name.lower() for keyword in ['ghid', 'alegere', 'cum să']):
                    combined['buying_guides'].extend(tab_data.get('descriptions', []))
                elif any(keyword in tab_name.lower() for keyword in ['instalare', 'montaj']):
                    combined['installation_info'].extend(tab_data.get('descriptions', []))
        
        # Deduplică și limitează
        combined['total_descriptions'] = list(dict.fromkeys(combined['total_descriptions']))[:15]
        combined['comprehensive_faqs'] = list(dict.fromkeys(combined['comprehensive_faqs']))[:10]
        combined['buying_guides'] = list(dict.fromkeys(combined['buying_guides']))[:8]
        combined['installation_info'] = list(dict.fromkeys(combined['installation_info']))[:6]
        combined['all_headings'] = list(dict.fromkeys(combined['all_headings']))[:20]
        
        return combined

    def test_complete_extraction(self, category_id="ghidoline"):
        """Testează extragerea completă"""
        data = self.load_categories()
        if not data:
            return
        
        test_category = None
        for cat in data.get('categories', []):
            if cat.get('id') == category_id:
                test_category = cat
                break
        
        if not test_category:
            logger.error(f"❌ Nu s-a găsit categoria {category_id}")
            return
        
        url = test_category.get('url', '')
        logger.info(f"🧪 Extrag conținut complet pentru: {category_id}")
        logger.info(f"📍 URL: {url}")
        
        extracted_data = self.extract_complete_content(url, category_id)
        
        if extracted_data:
            main = extracted_data['main_content']
            tabs = extracted_data['tab_content']
            combined = extracted_data['comprehensive_data']
            
            logger.info(f"\n📊 REZULTATE EXTRAGERE COMPLETĂ:")
            logger.info(f"📄 Conținut principal - Descrieri: {len(main['descriptions'])}")
            logger.info(f"📋 Taburi accesate: {len(tabs)}")
            logger.info(f"🔧 Specificații tehnice: {len(combined['complete_specs'])}")
            logger.info(f"❓ FAQ-uri găsite: {len(combined['comprehensive_faqs'])}")
            logger.info(f"📖 Ghiduri de alegere: {len(combined['buying_guides'])}")
            logger.info(f"🛠️ Info instalare: {len(combined['installation_info'])}")
            logger.info(f"🏷️ Mărci găsite: {combined['brand_info']}")
            logger.info(f"📦 Produse: {combined['product_count']}")
            
            if tabs:
                logger.info(f"\n📋 TABURI ACCESATE:")
                for tab_name in tabs.keys():
                    logger.info(f"   - {tab_name}")
            
            if combined['comprehensive_faqs']:
                logger.info(f"\n❓ EXEMPLE FAQ-URI:")
                for i, faq in enumerate(combined['comprehensive_faqs'][:3], 1):
                    logger.info(f"   {i}. {faq}")
            
            if combined['complete_specs']:
                logger.info(f"\n🔧 EXEMPLE SPECIFICAȚII:")
                for key, value in list(combined['complete_specs'].items())[:3]:
                    logger.info(f"   {key}: {value}")
            
            # Salvează rezultatele
            if 'content_structure' not in test_category:
                test_category['content_structure'] = {}
            
            test_category['content_structure']['complete_extracted_content'] = extracted_data
            
            self.save_categories(data)
            logger.info(f"\n✅ Conținut complet salvat pentru categoria {category_id}!")
            
            return extracted_data
        
        return None

    def process_all_categories_complete(self):
        """Procesează toate categoriile cu extragere completă"""
        data = self.load_categories()
        if not data:
            return
        
        categories = data.get('categories', [])
        categories_to_process = [
            cat for cat in categories 
            if cat.get('id') not in self.processed_categories
        ]
        
        logger.info(f"🚀 Începe extragerea completă pentru {len(categories_to_process)} categorii")
        
        processed_count = 0
        for i, category in enumerate(categories_to_process, 1):
            category_id = category.get('id', 'unknown')
            url = category.get('url', '')
            
            if not url:
                logger.warning(f"⚠️ URL lipsă pentru {category_id}")
                continue
            
            logger.info(f"\n📋 Procesez categoria {i}/{len(categories_to_process)}: {category_id}")
            
            extracted_data = self.extract_complete_content(url, category_id)
            
            if extracted_data:
                if 'content_structure' not in category:
                    category['content_structure'] = {}
                
                category['content_structure']['complete_extracted_content'] = extracted_data
                
                combined = extracted_data['comprehensive_data']
                
                # Actualizează numărul de produse
                if combined['product_count'] > 0:
                    if ('schema_markup' in category['content_structure'] and 
                        'collection_page' in category['content_structure']['schema_markup']):
                        category['content_structure']['schema_markup']['collection_page']['numberOfItems'] = combined['product_count']
                
                processed_count += 1
                
                logger.info(f"✅ Complet extras pentru {category_id}:")
                logger.info(f"   📊 Produse: {combined['product_count']}")
                logger.info(f"   📋 Taburi: {len(extracted_data['tab_content'])}")
                logger.info(f"   ❓ FAQ-uri: {len(combined['comprehensive_faqs'])}")
                logger.info(f"   🔧 Specificații: {len(combined['complete_specs'])}")
                
                # Salvează progresul
                if processed_count % 5 == 0:
                    self.save_categories(data)
                    logger.info(f"💾 Progres salvat: {processed_count}/{len(categories_to_process)}")
            
            time.sleep(2)  # Pauză între cereri
        
        # Salvează final
        self.save_categories(data)
        logger.info(f"\n🎉 FINALIZAT COMPLET! Procesate {processed_count} categorii!")

if __name__ == "__main__":
    extractor = FinalContentExtractor(
        r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    )
    
    # Test pentru o categorie
    print("🧪 Testez extragerea completă cu taburi...")
    extractor.test_complete_extraction("ghidoline")
