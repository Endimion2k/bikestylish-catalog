#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script alternativ pentru testarea structurii taburilor pe BikeStylish
Folosește requests cu sesiuni și simuleaza interacțiunea cu taburile
"""

import json
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TabContentAnalyzer:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def load_categories(self):
        """Încarcă categoriile din JSON"""
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
            return True
        except Exception as e:
            logger.error(f"Eroare la salvarea JSON: {e}")
            return False

    def analyze_page_structure(self, url):
        """Analizează structura paginii pentru a detecta taburi și conținut dinamic"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'has_javascript_tabs': False,
                'tab_elements': [],
                'content_sections': [],
                'ajax_endpoints': [],
                'data_attributes': [],
                'hidden_content': [],
                'all_visible_content': {}
            }
            
            # Caută indicatori de taburi JavaScript
            tab_indicators = [
                'class*="tab"', 'class*="nav"', 'data-tab', 'data-toggle',
                'role="tab"', 'aria-selected', 'class*="active"'
            ]
            
            for indicator in tab_indicators:
                elements = soup.select(f'[{indicator}]')
                if elements:
                    analysis['has_javascript_tabs'] = True
                    for elem in elements:
                        analysis['tab_elements'].append({
                            'tag': elem.name,
                            'text': elem.get_text().strip()[:50],
                            'attributes': dict(elem.attrs),
                            'classes': elem.get('class', [])
                        })
            
            # Caută conținut ascuns (care ar putea fi în taburi)
            hidden_elements = soup.find_all(['div', 'section'], 
                style=re.compile(r'display:\s*none|visibility:\s*hidden', re.I))
            
            for hidden in hidden_elements:
                content = hidden.get_text().strip()
                if len(content) > 50:
                    analysis['hidden_content'].append({
                        'content': content[:300],
                        'classes': hidden.get('class', []),
                        'id': hidden.get('id', '')
                    })
            
            # Caută atribute data-* care ar putea indica conținut dinamic
            all_elements = soup.find_all()
            for elem in all_elements[:50]:  # Limitează numărul de elemente verificate
                if hasattr(elem, 'attrs') and elem.attrs:
                    data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
                    if data_attrs:
                        analysis['data_attributes'].append({
                            'tag': elem.name,
                            'data_attrs': data_attrs,
                            'text': elem.get_text().strip()[:100]
                        })
                        if len(analysis['data_attributes']) >= 10:
                            break
            
            # Extrage tot conținutul vizibil
            analysis['all_visible_content'] = self._extract_all_content(soup)
            
            # Caută script-uri care ar putea încărca conținut dinamic
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.string or ''
                if any(keyword in script_text.lower() for keyword in ['ajax', 'tab', 'load', 'show', 'hide']):
                    # Caută URL-uri în script
                    urls = re.findall(r'["\']([^"\']*\.php[^"\']*)["\']', script_text)
                    analysis['ajax_endpoints'].extend(urls)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Eroare la analiza paginii {url}: {e}")
            return None

    def _extract_all_content(self, soup):
        """Extrage tot conținutul disponibil din pagină"""
        content = {
            'main_headings': [],
            'all_paragraphs': [],
            'lists_content': [],
            'table_data': [],
            'potential_faqs': [],
            'technical_info': []
        }
        
        # Headings
        for h in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            content['main_headings'].append({
                'level': h.name,
                'text': h.get_text().strip(),
                'classes': h.get('class', [])
            })
        
        # Paragrafe
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 30:
                content['all_paragraphs'].append(text[:300])
        
        # Liste
        for ul in soup.find_all(['ul', 'ol']):
            items = [li.get_text().strip() for li in ul.find_all('li')]
            if items:
                content['lists_content'].append(items)
        
        # Tabele
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            if rows:
                content['table_data'].append(rows)
        
        # Potențiale FAQ-uri (întrebări)
        all_text = soup.get_text()
        question_patterns = [
            r'[A-ZÀ-ÿ][^.!?]*\?',
            r'[Cc]e [^.!?]*\?',
            r'[Cc]um [^.!?]*\?',
            r'[Cc]are [^.!?]*\?'
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, all_text)
            for match in matches:
                if len(match) > 15 and len(match) < 150:
                    content['potential_faqs'].append(match.strip())
                    if len(content['potential_faqs']) >= 10:
                        break
        
        # Informații tehnice (numere, specificații)
        tech_patterns = [
            r'\d+\s*(?:mm|cm|kg|g|lumeni|mAh|V|A|W)',
            r'[A-Z]{2,}\s*\d+',
            r'IP\d{2}',
            r'USB-[AC]',
            r'LED',
            r'Li-ion'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            content['technical_info'].extend(matches[:10])
        
        return content

    def try_access_dynamic_content(self, url, category_id):
        """Încearcă să acceseze conținut dinamic prin diverse metode"""
        
        # Analizează structura principală
        analysis = self.analyze_page_structure(url)
        if not analysis:
            return None
        
        dynamic_content = {
            'base_analysis': analysis,
            'additional_requests': [],
            'combined_content': {}
        }
        
        # Încearcă să facă cereri către endpoint-urile AJAX găsite
        for endpoint in analysis['ajax_endpoints'][:3]:
            try:
                if endpoint.startswith('/'):
                    full_url = f"https://www.bikestylish.ro{endpoint}"
                else:
                    full_url = endpoint
                
                logger.info(f"🔗 Încerc endpoint AJAX: {full_url}")
                
                response = self.session.get(full_url, timeout=15)
                if response.status_code == 200:
                    content_soup = BeautifulSoup(response.content, 'html.parser')
                    extra_content = self._extract_all_content(content_soup)
                    dynamic_content['additional_requests'].append({
                        'url': full_url,
                        'content': extra_content
                    })
                    logger.info(f"✅ Content suplimentar extras din AJAX")
                
            except Exception as e:
                logger.warning(f"⚠️ Eroare la accesarea endpoint-ului {endpoint}: {e}")
        
        # Combină tot conținutul
        all_content = analysis['all_visible_content']
        
        for req in dynamic_content['additional_requests']:
            extra = req['content']
            all_content['all_paragraphs'].extend(extra['all_paragraphs'])
            all_content['lists_content'].extend(extra['lists_content'])
            all_content['table_data'].extend(extra['table_data'])
            all_content['potential_faqs'].extend(extra['potential_faqs'])
            all_content['technical_info'].extend(extra['technical_info'])
        
        dynamic_content['combined_content'] = all_content
        
        return dynamic_content

    def test_category_analysis(self, category_id="ghidoline"):
        """Testează analiza pentru o categorie"""
        data = self.load_categories()
        if not data:
            return
        
        # Găsește categoria
        test_category = None
        for cat in data.get('categories', []):
            if cat.get('id') == category_id:
                test_category = cat
                break
        
        if not test_category:
            logger.error(f"❌ Nu s-a găsit categoria {category_id}")
            return
        
        url = test_category.get('url', '')
        logger.info(f"🧪 Analizez categoria: {category_id}")
        logger.info(f"📍 URL: {url}")
        
        # Analizează structura
        dynamic_content = self.try_access_dynamic_content(url, category_id)
        
        if dynamic_content:
            analysis = dynamic_content['base_analysis']
            combined = dynamic_content['combined_content']
            
            logger.info(f"\n📊 ANALIZA STRUCTURII PAGINII:")
            logger.info(f"🔗 Are taburi JavaScript: {analysis['has_javascript_tabs']}")
            logger.info(f"📋 Elemente tab găsite: {len(analysis['tab_elements'])}")
            logger.info(f"🔒 Conținut ascuns: {len(analysis['hidden_content'])}")
            logger.info(f"📡 Endpoint-uri AJAX: {len(analysis['ajax_endpoints'])}")
            logger.info(f"🏷️ Atribute data-*: {len(analysis['data_attributes'])}")
            
            logger.info(f"\n📝 CONȚINUT EXTRAS:")
            logger.info(f"📰 Headings: {len(combined['main_headings'])}")
            logger.info(f"📄 Paragrafe: {len(combined['all_paragraphs'])}")
            logger.info(f"📋 Liste: {len(combined['lists_content'])}")
            logger.info(f"📊 Tabele: {len(combined['table_data'])}")
            logger.info(f"❓ Potențiale FAQ-uri: {len(combined['potential_faqs'])}")
            logger.info(f"🔧 Info tehnice: {len(combined['technical_info'])}")
            
            # Afișează exemple
            if analysis['tab_elements']:
                logger.info(f"\n📋 ELEMENTE TAB DETECTATE:")
                for i, tab in enumerate(analysis['tab_elements'][:3], 1):
                    logger.info(f"   {i}. {tab['tag']}: '{tab['text']}' (clase: {tab['classes']})")
            
            if combined['potential_faqs']:
                logger.info(f"\n❓ EXEMPLE FAQ-URI GĂSITE:")
                for i, faq in enumerate(combined['potential_faqs'][:3], 1):
                    logger.info(f"   {i}. {faq}")
            
            if combined['technical_info']:
                logger.info(f"\n🔧 INFO TEHNICE GĂSITE:")
                logger.info(f"   {', '.join(set(combined['technical_info'][:10]))}")
            
            # Salvează rezultatele
            if 'content_structure' not in test_category:
                test_category['content_structure'] = {}
            
            test_category['content_structure']['advanced_page_analysis'] = dynamic_content
            
            self.save_categories(data)
            logger.info(f"\n✅ Analiza avansată salvată pentru categoria {category_id}!")
            
            return dynamic_content
        
        return None

if __name__ == "__main__":
    analyzer = TabContentAnalyzer(
        r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    )
    
    # Testează analiza
    print("🧪 Analizez structura paginii cu taburi...")
    analyzer.test_category_analysis("ghidoline")
