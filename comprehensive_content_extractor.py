#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script complet pentru extragerea conținutului detaliat din toate paginile de categorii BikeStylish.
Extrage: FAQ-uri reale, ghiduri de alegere, specificații tehnice, informații de montaj, etc.
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

class ComprehensiveContentExtractor:
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

    def extract_comprehensive_content(self, url, category_id):
        """Extrage conținut comprehensiv din pagină"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Structura de conținut extras
            content = {
                'extraction_timestamp': datetime.now().isoformat(),
                'source_url': url,
                'page_structure': self._extract_page_structure(soup),
                'product_information': self._extract_product_info(soup),
                'real_faqs': self._extract_real_faqs(soup),
                'buying_guides': self._extract_buying_guides(soup),
                'technical_details': self._extract_technical_details(soup),
                'installation_guides': self._extract_installation_guides(soup),
                'brand_information': self._extract_brand_info(soup),
                'price_information': self._extract_price_info(soup),
                'features_benefits': self._extract_features_benefits(soup),
                'compatibility_info': self._extract_compatibility_info(soup)
            }
            
            return content
            
        except Exception as e:
            logger.error(f"Eroare la extragerea conținutului pentru {category_id}: {e}")
            return None

    def _extract_page_structure(self, soup):
        """Extrage structura paginii"""
        return {
            'title': soup.title.get_text().strip() if soup.title else '',
            'h1_headings': [h.get_text().strip() for h in soup.find_all('h1')],
            'h2_headings': [h.get_text().strip() for h in soup.find_all('h2')][:15],
            'h3_headings': [h.get_text().strip() for h in soup.find_all('h3')][:10],
            'main_sections': [div.get('class', [''])[0] for div in soup.find_all('div') if div.get('class')][:20]
        }

    def _extract_product_info(self, soup):
        """Extrage informații despre produse"""
        info = {
            'total_products': 0,
            'product_categories': [],
            'featured_products': []
        }
        
        # Numărul total de produse
        count_patterns = [
            r'din\s+(\d+)\s+produs',
            r'(\d+)\s+produse',
            r'Afiseaza.*?din\s+(\d+)'
        ]
        
        page_text = soup.get_text()
        for pattern in count_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                info['total_products'] = int(match.group(1))
                break
        
        # Produse recomandate/featured
        product_elements = soup.find_all(['div', 'article'], class_=re.compile(r'product|item', re.I))
        for prod in product_elements[:5]:
            title_elem = prod.find(['h1', 'h2', 'h3', 'a'])
            if title_elem:
                title = title_elem.get_text().strip()
                if len(title) > 10 and len(title) < 100:
                    info['featured_products'].append(title)
        
        return info

    def _extract_real_faqs(self, soup):
        """Extrage FAQ-uri reale din pagină"""
        faqs = []
        
        # Caută întrebări în textul paginii
        page_text = soup.get_text()
        sentences = re.split(r'[.!?]', page_text)
        
        question_patterns = [
            r'^(Ce|Cum|Care|De ce|Când|Unde|Cât|Cine).*\?',
            r'.*\b(alegi|alegere|important|recomandat|trebuie|sfat|sfaturi)\b.*',
            r'.*\b(compatibil|instalare|montaj|întreținere|durabilitate)\b.*'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                for pattern in question_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        # Găsește răspunsul (următoarea propoziție sau paragraph)
                        sentence_index = sentences.index(sentence)
                        if sentence_index + 1 < len(sentences):
                            potential_answer = sentences[sentence_index + 1].strip()
                            if len(potential_answer) > 30:
                                faqs.append({
                                    'question': sentence,
                                    'answer': potential_answer[:300] + '...' if len(potential_answer) > 300 else potential_answer
                                })
                                break
        
        # Caută în structuri HTML specifice
        faq_containers = soup.find_all(['div', 'section'], class_=re.compile(r'faq|question|qa', re.I))
        for container in faq_containers:
            questions = container.find_all(['h2', 'h3', 'h4', 'dt'])
            for q in questions:
                q_text = q.get_text().strip()
                if '?' in q_text or any(word in q_text.lower() for word in ['cum', 'ce', 'care']):
                    answer_elem = q.find_next_sibling(['p', 'div', 'dd'])
                    if answer_elem:
                        faqs.append({
                            'question': q_text,
                            'answer': answer_elem.get_text().strip()[:300]
                        })
        
        return faqs[:8]  # Maxim 8 FAQ-uri reale

    def _extract_buying_guides(self, soup):
        """Extrage ghiduri de cumpărare și alegere"""
        guides = []
        
        # Caută ghiduri în headings
        guide_headings = soup.find_all(['h2', 'h3'], string=re.compile(r'ghid|alegere|cum să alegi|guide|recomandări', re.I))
        
        for heading in guide_headings:
            guide_content = []
            current = heading.find_next_sibling()
            
            while current and current.name in ['p', 'ul', 'ol', 'div']:
                text = current.get_text().strip()
                if len(text) > 30:
                    guide_content.append(text[:250])
                    if len(guide_content) >= 3:
                        break
                current = current.find_next_sibling()
            
            if guide_content:
                guides.append({
                    'title': heading.get_text().strip(),
                    'content': guide_content
                })
        
        # Caută și în conținutul general tips-uri de alegere
        page_text = soup.get_text()
        tip_patterns = [
            r'[Tt]rebuie să.*?[.!]',
            r'[Rr]ecomandat.*?[.!]',
            r'[Ii]mportant.*?[.!]',
            r'[Aa]tenție.*?[.!]'
        ]
        
        tips = []
        for pattern in tip_patterns:
            matches = re.findall(pattern, page_text)
            for match in matches[:3]:
                if len(match) > 20:
                    tips.append(match.strip())
        
        if tips:
            guides.append({
                'title': 'Sfaturi Importante',
                'content': tips
            })
        
        return guides[:5]  # Maxim 5 ghiduri

    def _extract_technical_details(self, soup):
        """Extrage detalii tehnice"""
        tech_details = {}
        
        # Caută în tabele
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    if key and value and len(key) < 50:
                        tech_details[key] = value
        
        # Caută specificații în liste
        spec_lists = soup.find_all(['ul', 'ol'])
        for spec_list in spec_lists:
            items = spec_list.find_all('li')
            for item in items:
                text = item.get_text().strip()
                if ':' in text:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        tech_details[parts[0].strip()] = parts[1].strip()
        
        # Caută termeni tehnici specifici
        tech_terms = ['LED', 'USB', 'Bluetooth', 'GPS', 'Li-ion', 'mAh', 'lumeni', 
                     'IPX', 'kg', 'gram', 'mm', 'cm', 'inch', 'Nm']
        
        page_text = soup.get_text()
        found_specs = {}
        for term in tech_terms:
            pattern = f'{term}[:\s]*([^.!?]*)'
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                found_specs[term] = matches[0].strip()[:100]
        
        tech_details.update(found_specs)
        
        return dict(list(tech_details.items())[:15])  # Maxim 15 specificații

    def _extract_installation_guides(self, soup):
        """Extrage ghiduri de instalare/montaj"""
        installation_info = []
        
        # Caută secțiuni de instalare
        install_headings = soup.find_all(['h2', 'h3'], string=re.compile(r'instalare|montaj|install|assembly', re.I))
        
        for heading in install_headings:
            steps = []
            current = heading.find_next_sibling()
            
            while current and len(steps) < 5:
                if current.name in ['ol', 'ul']:
                    items = current.find_all('li')
                    for item in items:
                        step_text = item.get_text().strip()
                        if len(step_text) > 20:
                            steps.append(step_text[:200])
                elif current.name == 'p':
                    text = current.get_text().strip()
                    if any(word in text.lower() for word in ['pas', 'step', 'urmă', 'apoi']):
                        steps.append(text[:200])
                
                current = current.find_next_sibling()
            
            if steps:
                installation_info.append({
                    'section': heading.get_text().strip(),
                    'steps': steps
                })
        
        return installation_info[:3]  # Maxim 3 secțiuni

    def _extract_brand_info(self, soup):
        """Extrage informații despre mărci"""
        brands = {}
        common_brands = ['M-WAVE', 'SXT', 'SHIMANO', 'SUPER B', 'VENTURA', 'NECO', 
                        'MOON', 'VELO', 'EXTEND', 'NOVATEC', 'CICLO BONIN', 'ZOOM', 
                        'AUTHOR', 'DEDA', 'BETO', 'CST', 'BAFANG']
        
        page_text = soup.get_text().upper()
        for brand in common_brands:
            if brand in page_text:
                # Găsește context despre marcă
                sentences = re.split(r'[.!?]', soup.get_text())
                for sentence in sentences:
                    if brand.lower() in sentence.lower():
                        brands[brand] = sentence.strip()[:200]
                        break
        
        return brands

    def _extract_price_info(self, soup):
        """Extrage informații despre prețuri"""
        price_info = {
            'price_range': '',
            'currency': 'RON',
            'found_prices': []
        }
        
        # Caută prețuri în pagină
        price_patterns = [
            r'(\d+)[,.]?(\d*)\s*(?:RON|lei)',
            r'(\d+)[,.]?(\d*)\s*(?:EUR|euro)',
            r'de la\s*(\d+)',
            r'până la\s*(\d+)'
        ]
        
        page_text = soup.get_text()
        prices = []
        
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    price = int(match[0])
                else:
                    price = int(match)
                if 10 <= price <= 10000:  # Filtrare prețuri rezonabile
                    prices.append(price)
        
        if prices:
            price_info['found_prices'] = list(set(prices))[:10]
            price_info['price_range'] = f"{min(prices)}-{max(prices)} RON"
        
        return price_info

    def _extract_features_benefits(self, soup):
        """Extrage caracteristici și beneficii"""
        features = []
        
        # Caută liste de caracteristici
        feature_indicators = ['caracteristici', 'beneficii', 'avantaje', 'features']
        
        for indicator in feature_indicators:
            sections = soup.find_all(text=re.compile(indicator, re.IGNORECASE))
            for section in sections:
                parent = section.find_parent()
                if parent:
                    lists = parent.find_all(['ul', 'ol'])
                    for lst in lists:
                        items = lst.find_all('li')
                        for item in items:
                            feature_text = item.get_text().strip()
                            if len(feature_text) > 15:
                                features.append(feature_text[:150])
        
        # Caută și în emoji/bullet points
        emoji_features = soup.find_all(text=re.compile(r'[✓✅🔧⚙️💡🎯]'))
        for feature in emoji_features[:5]:
            text = feature.strip()
            if len(text) > 20:
                features.append(text[:150])
        
        return features[:12]  # Maxim 12 caracteristici

    def _extract_compatibility_info(self, soup):
        """Extrage informații de compatibilitate"""
        compatibility = []
        
        compat_keywords = ['compatibil', 'compatible', 'potrivit', 'se potrivește', 'funcționează cu']
        page_text = soup.get_text()
        sentences = re.split(r'[.!?]', page_text)
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in compat_keywords):
                if len(sentence.strip()) > 20:
                    compatibility.append(sentence.strip()[:200])
                if len(compatibility) >= 5:
                    break
        
        return compatibility

    def process_all_categories(self):
        """Procesează toate categoriile"""
        data = self.load_categories()
        if not data:
            return
        
        categories = data.get('categories', [])
        if not categories:
            logger.error("Nu s-au găsit categorii în JSON")
            return
        
        # Filtrează categoriile care nu au fost procesate manual
        categories_to_process = [
            cat for cat in categories 
            if cat.get('id') not in self.processed_categories
        ]
        
        logger.info(f"🚀 Începe extragerea conținutului detaliat pentru {len(categories_to_process)} categorii")
        
        processed_count = 0
        for i, category in enumerate(categories_to_process, 1):
            category_id = category.get('id', 'unknown')
            url = category.get('url', '')
            
            if not url:
                logger.warning(f"⚠️ URL lipsă pentru categoria {category_id}")
                continue
            
            logger.info(f"\n📋 Procesez categoria {i}/{len(categories_to_process)}: {category_id}")
            
            # Extrage conținutul comprehensiv
            extracted_content = self.extract_comprehensive_content(url, category_id)
            
            if extracted_content:
                # Actualizează categoria cu conținutul extras
                if 'content_structure' not in category:
                    category['content_structure'] = {}
                
                category['content_structure']['web_extracted_comprehensive'] = extracted_content
                
                # Actualizează și numărul de produse în schema
                product_count = extracted_content['product_information']['total_products']
                if product_count > 0:
                    if ('schema_markup' in category['content_structure'] and 
                        'collection_page' in category['content_structure']['schema_markup']):
                        category['content_structure']['schema_markup']['collection_page']['numberOfItems'] = product_count
                
                processed_count += 1
                
                # Log sumar
                logger.info(f"✅ Conținut extras pentru {category_id}:")
                logger.info(f"   📊 Produse: {product_count}")
                logger.info(f"   ❓ FAQ-uri: {len(extracted_content['real_faqs'])}")
                logger.info(f"   📖 Ghiduri: {len(extracted_content['buying_guides'])}")
                logger.info(f"   🔧 Detalii tehnice: {len(extracted_content['technical_details'])}")
                logger.info(f"   🏷️ Mărci: {len(extracted_content['brand_information'])}")
                
                # Salvează progresul la fiecare 3 categorii
                if processed_count % 3 == 0:
                    self.save_categories(data)
                    logger.info(f"💾 Progres salvat: {processed_count}/{len(categories_to_process)}")
            
            else:
                logger.error(f"❌ Eșec extragere pentru {category_id}")
            
            # Pauză între cereri
            time.sleep(2)
        
        # Salvează versiunea finală
        if self.save_categories(data):
            logger.info(f"\n🎉 FINALIZAT! Procesate {processed_count} categorii cu conținut complet!")
            logger.info(f"📋 Fiecare categorie conține acum:")
            logger.info(f"   - FAQ-uri reale din site")
            logger.info(f"   - Ghiduri de alegere și cumpărare")
            logger.info(f"   - Specificații tehnice detaliate")
            logger.info(f"   - Informații de instalare/montaj")
            logger.info(f"   - Detalii despre mărci și compatibilitate")
        else:
            logger.error("❌ Eroare la salvarea finală!")

if __name__ == "__main__":
    extractor = ComprehensiveContentExtractor(
        r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    )
    extractor.process_all_categories()
