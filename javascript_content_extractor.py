#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script avansat cu Selenium pentru extragerea conținutului din taburi JavaScript
BikeStylish folosește taburi dinamice care se încarcă cu JS
"""

import json
import time
import re
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JavaScriptContentExtractor:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.driver = None
        
        # Categorii deja procesate manual
        self.processed_categories = {
            'accesorii-bicicleta', 'accesorii', 'remorci-transport-copii',
            'roti-ajutatoare', 'scaune-pentru-copii', 'transport-si-depozitare',
            'reflectorizante', 'articole-copii-roti-ajutatoare',
            'parti-ghidoane-si-barend-extensiighidon', 'cricuri-de-mijloc',
            'cosuri-pentru-biciclete'
        }

    def setup_driver(self):
        """Configurează driver-ul Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Rulează în background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("✅ Driver Selenium configurat cu succes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Eroare la configurarea driver-ului: {e}")
            return False

    def close_driver(self):
        """Închide driver-ul"""
        if self.driver:
            self.driver.quit()

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

    def extract_tab_content(self, url, category_id):
        """Extrage conținut din toate taburile unei pagini"""
        try:
            logger.info(f"🌐 Accesez pagina: {url}")
            self.driver.get(url)
            
            # Așteaptă ca pagina să se încarce
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Găsește toate taburile
            tab_content = {
                'main_content': '',
                'tabs_content': {},
                'all_text_content': '',
                'extracted_sections': {}
            }
            
            # Extrage conținutul principal fără taburi
            main_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            tab_content['main_content'] = main_soup.get_text()
            
            # Caută taburi (diferite selectori posibili)
            tab_selectors = [
                '.tabs .tab',
                '.tab-navigation .tab',
                '.nav-tabs .nav-item',
                '[role="tab"]',
                '.tab-button',
                '.tab-link',
                'a[data-tab]',
                'button[data-tab]'
            ]
            
            tabs_found = []
            for selector in tab_selectors:
                try:
                    tabs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if tabs:
                        tabs_found = tabs
                        logger.info(f"📋 Găsite {len(tabs)} taburi cu selectorul: {selector}")
                        break
                except:
                    continue
            
            if not tabs_found:
                # Încearcă să găsească prin text
                try:
                    common_tab_texts = ['Descriere', 'Specificații', 'Ghid alegere', 'FAQ', 'Instalare', 'Caracteristici', 'Detalii']
                    for text in common_tab_texts:
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                        for elem in elements:
                            if elem.tag_name in ['a', 'button', 'div'] and elem.is_displayed():
                                tabs_found.append(elem)
                    
                    if tabs_found:
                        logger.info(f"📋 Găsite {len(tabs_found)} taburi prin text")
                except:
                    pass
            
            # Dacă nu găsește taburi, extrage tot conținutul disponibil
            if not tabs_found:
                logger.info("⚠️ Nu s-au găsit taburi, extrag conținutul complet al paginii")
                tab_content['all_text_content'] = main_soup.get_text()
                tab_content['extracted_sections'] = self._extract_sections_from_html(main_soup)
            else:
                # Procesează fiecare tab
                for i, tab in enumerate(tabs_found[:8]):  # Maxim 8 taburi
                    try:
                        tab_name = f"tab_{i+1}"
                        
                        # Încearcă să obțină numele tabului
                        try:
                            tab_text = tab.text.strip()
                            if tab_text:
                                tab_name = tab_text[:30]
                        except:
                            pass
                        
                        logger.info(f"🔍 Procesez tabul: {tab_name}")
                        
                        # Click pe tab
                        self.driver.execute_script("arguments[0].scrollIntoView();", tab)
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", tab)
                        time.sleep(2)  # Așteaptă ca conținutul să se încarce
                        
                        # Extrage conținutul după click
                        updated_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        tab_content['tabs_content'][tab_name] = {
                            'html_content': str(updated_soup),
                            'text_content': updated_soup.get_text(),
                            'extracted_data': self._extract_sections_from_html(updated_soup)
                        }
                        
                        logger.info(f"✅ Conținut extras din tabul: {tab_name}")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Eroare la procesarea tabului {i+1}: {e}")
                        continue
            
            # Extrage informații finale
            final_content = self._compile_final_content(tab_content)
            
            return final_content
            
        except Exception as e:
            logger.error(f"❌ Eroare la extragerea conținutului pentru {category_id}: {e}")
            return None

    def _extract_sections_from_html(self, soup):
        """Extrage secțiuni specifice din HTML"""
        sections = {
            'faqs': [],
            'specifications': {},
            'guides': [],
            'features': [],
            'installation': [],
            'descriptions': []
        }
        
        # FAQ-uri
        faq_elements = soup.find_all(text=re.compile(r'[Cc]e |[Cc]um |[Cc]are |[Dd]e ce |\?'))
        for faq in faq_elements:
            faq_text = faq.strip()
            if len(faq_text) > 20 and '?' in faq_text:
                # Găsește răspunsul
                parent = faq.parent if hasattr(faq, 'parent') else None
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        answer = next_elem.get_text().strip()[:300]
                        sections['faqs'].append({
                            'question': faq_text,
                            'answer': answer
                        })
                        if len(sections['faqs']) >= 8:
                            break
        
        # Specificații (tabele, liste)
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if key and value:
                        sections['specifications'][key] = value
        
        # Caracteristici (liste cu bullet points)
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            for item in items:
                text = item.get_text().strip()
                if len(text) > 15:
                    sections['features'].append(text[:200])
                    if len(sections['features']) >= 15:
                        break
        
        # Ghiduri și descrieri
        headings = soup.find_all(['h2', 'h3'], string=re.compile(r'ghid|alegere|cum să|descriere|instalare', re.IGNORECASE))
        for heading in headings:
            content = []
            current = heading.find_next_sibling()
            while current and len(content) < 5:
                if current.name in ['p', 'div']:
                    text = current.get_text().strip()
                    if len(text) > 30:
                        content.append(text[:300])
                current = current.find_next_sibling() if current else None
            
            if content:
                if 'ghid' in heading.get_text().lower() or 'alegere' in heading.get_text().lower():
                    sections['guides'].extend(content)
                elif 'instalare' in heading.get_text().lower():
                    sections['installation'].extend(content)
                else:
                    sections['descriptions'].extend(content)
        
        return sections

    def _compile_final_content(self, tab_content):
        """Compilează conținutul final din toate taburile"""
        compiled = {
            'extraction_timestamp': datetime.now().isoformat(),
            'tabs_processed': len(tab_content.get('tabs_content', {})),
            'comprehensive_faqs': [],
            'detailed_specifications': {},
            'buying_guides': [],
            'installation_guides': [],
            'product_features': [],
            'technical_descriptions': [],
            'all_sections': {}
        }
        
        # Combină conținutul din toate taburile
        all_sections = {}
        
        # Procesează conținutul principal
        if tab_content.get('extracted_sections'):
            all_sections['main'] = tab_content['extracted_sections']
        
        # Procesează conținutul din taburi
        for tab_name, tab_data in tab_content.get('tabs_content', {}).items():
            all_sections[tab_name] = tab_data.get('extracted_data', {})
        
        # Combină FAQ-urile din toate taburile
        for section_name, section_data in all_sections.items():
            if 'faqs' in section_data:
                compiled['comprehensive_faqs'].extend(section_data['faqs'])
            if 'specifications' in section_data:
                compiled['detailed_specifications'].update(section_data['specifications'])
            if 'guides' in section_data:
                compiled['buying_guides'].extend(section_data['guides'])
            if 'installation' in section_data:
                compiled['installation_guides'].extend(section_data['installation'])
            if 'features' in section_data:
                compiled['product_features'].extend(section_data['features'])
            if 'descriptions' in section_data:
                compiled['technical_descriptions'].extend(section_data['descriptions'])
        
        # Deduplică și limitează
        compiled['comprehensive_faqs'] = compiled['comprehensive_faqs'][:10]
        compiled['detailed_specifications'] = dict(list(compiled['detailed_specifications'].items())[:20])
        compiled['buying_guides'] = list(set(compiled['buying_guides']))[:8]
        compiled['installation_guides'] = list(set(compiled['installation_guides']))[:6]
        compiled['product_features'] = list(set(compiled['product_features']))[:15]
        compiled['technical_descriptions'] = list(set(compiled['technical_descriptions']))[:10]
        
        compiled['all_sections'] = all_sections
        
        return compiled

    def test_single_category(self, category_id="ghidoline"):
        """Testează extragerea pentru o singură categorie"""
        if not self.setup_driver():
            return
        
        try:
            data = self.load_categories()
            if not data:
                return
            
            # Găsește categoria de test
            test_category = None
            for cat in data.get('categories', []):
                if cat.get('id') == category_id:
                    test_category = cat
                    break
            
            if not test_category:
                logger.error(f"❌ Nu s-a găsit categoria {category_id}")
                return
            
            url = test_category.get('url', '')
            logger.info(f"🧪 Testez categoria: {category_id}")
            logger.info(f"📍 URL: {url}")
            
            # Extrage conținutul
            extracted_content = self.extract_tab_content(url, category_id)
            
            if extracted_content:
                logger.info(f"\n📊 REZULTATE EXTRAGERE JAVASCRIPT:")
                logger.info(f"📋 Taburi procesate: {extracted_content['tabs_processed']}")
                logger.info(f"❓ FAQ-uri găsite: {len(extracted_content['comprehensive_faqs'])}")
                logger.info(f"🔧 Specificații: {len(extracted_content['detailed_specifications'])}")
                logger.info(f"📖 Ghiduri: {len(extracted_content['buying_guides'])}")
                logger.info(f"⚙️ Instalare: {len(extracted_content['installation_guides'])}")
                logger.info(f"✨ Caracteristici: {len(extracted_content['product_features'])}")
                
                # Afișează exemple
                if extracted_content['comprehensive_faqs']:
                    logger.info(f"\n📋 EXEMPLE FAQ-URI DIN TABURI:")
                    for i, faq in enumerate(extracted_content['comprehensive_faqs'][:3], 1):
                        logger.info(f"   {i}. Q: {faq.get('question', '')[:100]}")
                        logger.info(f"      A: {faq.get('answer', '')[:100]}")
                
                if extracted_content['detailed_specifications']:
                    logger.info(f"\n🔧 EXEMPLE SPECIFICAȚII:")
                    for key, value in list(extracted_content['detailed_specifications'].items())[:3]:
                        logger.info(f"   {key}: {value}")
                
                # Salvează în JSON
                if 'content_structure' not in test_category:
                    test_category['content_structure'] = {}
                
                test_category['content_structure']['javascript_extracted_content'] = extracted_content
                
                self.save_categories(data)
                logger.info(f"\n✅ Conținut JavaScript salvat pentru categoria {category_id}!")
            
        finally:
            self.close_driver()

    def process_all_categories_with_js(self):
        """Procesează toate categoriile cu JavaScript"""
        if not self.setup_driver():
            return
        
        try:
            data = self.load_categories()
            if not data:
                return
            
            categories = data.get('categories', [])
            categories_to_process = [
                cat for cat in categories 
                if cat.get('id') not in self.processed_categories
            ]
            
            logger.info(f"🚀 Începe extragerea JavaScript pentru {len(categories_to_process)} categorii")
            
            processed_count = 0
            for i, category in enumerate(categories_to_process, 1):
                category_id = category.get('id', 'unknown')
                url = category.get('url', '')
                
                if not url:
                    logger.warning(f"⚠️ URL lipsă pentru {category_id}")
                    continue
                
                logger.info(f"\n📋 Procesez categoria {i}/{len(categories_to_process)}: {category_id}")
                
                extracted_content = self.extract_tab_content(url, category_id)
                
                if extracted_content:
                    if 'content_structure' not in category:
                        category['content_structure'] = {}
                    
                    category['content_structure']['javascript_extracted_content'] = extracted_content
                    processed_count += 1
                    
                    logger.info(f"✅ JavaScript content extras pentru {category_id}")
                    
                    # Salvează progresul
                    if processed_count % 3 == 0:
                        self.save_categories(data)
                        logger.info(f"💾 Progres salvat: {processed_count}/{len(categories_to_process)}")
                
                time.sleep(3)  # Pauză între procesări
            
            # Salvează final
            self.save_categories(data)
            logger.info(f"\n🎉 FINALIZAT! Procesate {processed_count} categorii cu conținut JavaScript!")
            
        finally:
            self.close_driver()

if __name__ == "__main__":
    extractor = JavaScriptContentExtractor(
        r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    )
    
    # Testează pentru o categorie
    print("🧪 Rulez test pentru o categorie...")
    extractor.test_single_category("ghidoline")
