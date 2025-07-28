#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script specializat pentru extragerea FAQ-urilor cu răspunsuri dropdown din BikeStylish
Detectează și extrage conținut din acordeoane/collapse FAQ sections
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

class DropdownFAQExtractor:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
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

    def extract_dropdown_faqs(self, url, category_id):
        """Extrage FAQ-urile cu dropdown/acordeon și toate tipurile de conținut structurat"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            faq_data = {
                'extraction_timestamp': datetime.now().isoformat(),
                'source_url': url,
                'page_title': self._extract_page_title(soup),
                'meta_description': self._extract_meta_description(soup),
                'jsonld_schemas': self._extract_jsonld_schemas(soup),
                'dropdown_faqs': [],
                'bikestylish_faqs': [],
                'tab_content': [],
                'accordion_sections': [],
                'toggle_content': [],
                'hidden_answers': [],
                'breadcrumbs': self._extract_breadcrumbs(soup),
                'quick_stats': self._extract_quick_stats(soup),
                'product_grid': self._extract_product_grid(soup),
                'decision_tree': self._extract_decision_tree(soup),
                'nlp_summaries': self._extract_nlp_summaries(soup),
                'component_links': self._extract_component_links(soup),
                'cta_section': self._extract_cta_section(soup),
                'intro_content': self._extract_intro_content(soup),
                'knowledge_tables': self._extract_knowledge_tables(soup)
            }
            
            # Metodă 1: Caută structuri FAQ clasice cu dropdown
            faq_data['dropdown_faqs'] = self._extract_classic_dropdown_faqs(soup)
            
            # Metodă 1B: Caută structura specifică BikeStylish
            faq_data['bikestylish_faqs'] = self._extract_bikestylish_faqs(soup)
            
            # Metodă 1C: Caută conținutul din taburi
            faq_data['tab_content'] = self._extract_tab_content(soup)
            
            # Metodă 2: Caută acordeoane (accordion) generice
            faq_data['accordion_sections'] = self._extract_accordion_content(soup)
            
            # Metodă 3: Caută toggle/collapse content
            faq_data['toggle_content'] = self._extract_toggle_content(soup)
            
            # Metodă 4: Caută răspunsuri ascunse în attributele HTML
            faq_data['hidden_answers'] = self._extract_hidden_content(soup)
            
            # Combină toate FAQ-urile găsite
            all_faqs = self._combine_all_faqs(faq_data)
            faq_data['combined_faqs'] = all_faqs
            
            return faq_data
            
        except Exception as e:
            logger.error(f"Eroare la extragerea FAQ pentru {category_id}: {e}")
            return None

    def _extract_classic_dropdown_faqs(self, soup):
        """Extrage FAQ-uri din structuri dropdown clasice"""
        faqs = []
        
        # Selectori pentru FAQ dropdown-uri BikeStylish specifice
        faq_selectors = [
            '.faq-item-compact', '.faq-item', '.faq-question-compact', '.faq-question', 
            '.faq-section', '.accordion-item', '.qa-item', '.dropdown-faq',
            '[data-toggle="collapse"]', '[data-bs-toggle="collapse"]',
            '.collapse-trigger', '.expandable-question'
        ]
        
        for selector in faq_selectors:
            faq_elements = soup.select(selector)
            
            for element in faq_elements:
                faq_item = self._extract_single_faq_item(element)
                if faq_item:
                    faqs.append(faq_item)
        
        # Caută și prin atribute data-target
        data_toggle_elements = soup.find_all(attrs={'data-toggle': True})
        for element in data_toggle_elements:
            if element.get('data-toggle') in ['collapse', 'dropdown', 'tab']:
                faq_item = self._extract_single_faq_item(element)
                if faq_item:
                    faqs.append(faq_item)
        
        return faqs[:15]  # Limitează la 15 FAQ-uri

    def _extract_bikestylish_faqs(self, soup):
        """Extrage FAQ-uri din structura specifică BikeStylish"""
        faqs = []
        
        # Caută toate elementele faq-item-compact
        faq_items = soup.find_all('div', class_=re.compile(r'faq-item'))
        
        for faq_item in faq_items:
            # Caută întrebarea în faq-question-compact
            question_elem = faq_item.find(['button', 'div', 'span'], class_=re.compile(r'faq-question'))
            if not question_elem:
                # Caută și prin alte posibilități
                question_elem = faq_item.find(['h1', 'h2', 'h3', 'h4', 'h5', 'button', 'a', 'span'])
            
            # Caută răspunsul în faq-answer-compact
            answer_elem = faq_item.find(['div', 'p', 'span'], class_=re.compile(r'faq-answer'))
            if not answer_elem:
                # Caută și în următorul element
                answer_elem = faq_item.find_next_sibling()
                if not answer_elem:
                    # Caută în copiii faq_item
                    answer_elem = faq_item.find(['div', 'p'])
            
            if question_elem and answer_elem:
                question_text = question_elem.get_text().strip()
                answer_text = answer_elem.get_text().strip()
                
                # Validare FAQ
                if (len(question_text) > 10 and len(answer_text) > 20 and 
                    question_text != answer_text):
                    
                    faq_item = {
                        'question': question_text,
                        'answer': answer_text[:500] + '...' if len(answer_text) > 500 else answer_text,
                        'element_info': {
                            'container_classes': faq_item.get('class', []),
                            'question_classes': question_elem.get('class', []),
                            'answer_classes': answer_elem.get('class', []),
                            'answer_style': answer_elem.get('style', ''),
                            'structure_type': 'bikestylish_compact'
                        }
                    }
                    faqs.append(faq_item)
        
        return faqs[:10]

    def _extract_tab_content(self, soup):
        """Extrage conținut din taburile BikeStylish"""
        tab_content = []
        
        # Caută toate butoanele tab
        tab_buttons = soup.find_all(['button', 'a'], class_=re.compile(r'tab-button'))
        
        for tab_button in tab_buttons:
            tab_id = tab_button.get('data-tab', '')
            tab_name = tab_button.get_text().strip()
            
            if tab_id and tab_name:
                # Caută conținutul tabului
                tab_content_elem = soup.find('div', id=tab_id)
                if not tab_content_elem:
                    # Încearcă și cu alte selectori
                    tab_content_elem = soup.find('div', class_=re.compile(r'tab-content'), attrs={'data-tab': tab_id})
                
                if tab_content_elem:
                    # Extrage diferite tipuri de conținut din tab
                    tab_data = {
                        'tab_name': tab_name,
                        'tab_id': tab_id,
                        'features': [],
                        'text_content': '',
                        'lists': [],
                        'faqs': []
                    }
                    
                    # Extrage caracteristici din feature-grid
                    feature_grids = tab_content_elem.find_all('div', class_=re.compile(r'feature-grid'))
                    for grid in feature_grids:
                        feature_items = grid.find_all('div', class_=re.compile(r'feature-item'))
                        for item in feature_items:
                            feature_title = ''
                            feature_desc = ''
                            
                            # Caută titlul caracteristicii
                            title_elem = item.find(['h4', 'h5', 'h6', 'strong', 'b'])
                            if title_elem:
                                feature_title = title_elem.get_text().strip()
                            
                            # Caută descrierea
                            desc_elem = item.find('p')
                            if desc_elem:
                                feature_desc = desc_elem.get_text().strip()
                            elif not title_elem:  # Dacă nu am găsit titlu, ia tot textul
                                feature_desc = item.get_text().strip()
                            
                            if feature_title or feature_desc:
                                tab_data['features'].append({
                                    'title': feature_title,
                                    'description': feature_desc
                                })
                    
                    # Extrage textul general din tab
                    tab_text = tab_content_elem.get_text().strip()
                    # Curăță textul de caracteristici deja extrase
                    for feature in tab_data['features']:
                        if feature['title']:
                            tab_text = tab_text.replace(feature['title'], '')
                        if feature['description']:
                            tab_text = tab_text.replace(feature['description'], '')
                    
                    tab_data['text_content'] = tab_text[:300] if len(tab_text) > 10 else ''
                    
                    # Extrage liste din tab
                    lists = tab_content_elem.find_all(['ul', 'ol'])
                    for list_elem in lists:
                        list_items = [li.get_text().strip() for li in list_elem.find_all('li')]
                        if list_items:
                            tab_data['lists'].append(list_items)
                    
                    # Caută FAQ-uri în tab (întrebări cu răspunsuri)
                    potential_questions = tab_content_elem.find_all(string=re.compile(r'\?'))
                    for q_string in potential_questions[:3]:  # Maxim 3 întrebări per tab
                        parent = q_string.parent
                        if parent and len(q_string.strip()) > 15:
                            # Încearcă să găsească răspunsul
                            next_elem = parent.find_next_sibling(['p', 'div'])
                            if next_elem:
                                answer = next_elem.get_text().strip()
                                if len(answer) > 20 and '?' not in answer:
                                    tab_data['faqs'].append({
                                        'question': q_string.strip(),
                                        'answer': answer[:200]
                                    })
                    
                    tab_content.append(tab_data)
        
        return tab_content[:6]  # Maxim 6 taburi

    def _extract_single_faq_item(self, element):
        """Extrage o singură întrebare-răspuns FAQ"""
        faq_item = {'question': '', 'answer': '', 'element_info': {}}
        
        # Încearcă să găsească întrebarea
        question_text = ''
        
        # Dacă elementul însuși conține întrebarea
        element_text = element.get_text().strip()
        if '?' in element_text and len(element_text) < 200:
            question_text = element_text
        else:
            # Caută în copiii elementului
            question_elements = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'button', 'a', 'span'])
            for q_elem in question_elements:
                q_text = q_elem.get_text().strip()
                if ('?' in q_text or 
                    any(word in q_text.lower() for word in ['ce', 'cum', 'care', 'de ce', 'când', 'unde'])):
                    if 10 < len(q_text) < 200:
                        question_text = q_text
                        break
        
        if not question_text:
            return None
        
        # Încearcă să găsească răspunsul
        answer_text = ''
        
        # Metodă 1: Caută prin data-target sau href
        target_id = element.get('data-target', '').replace('#', '')
        if not target_id:
            target_id = element.get('href', '').replace('#', '')
        
        if target_id:
            target_element = element.find_parent().find(id=target_id) if element.find_parent() else None
            if not target_element:
                # Caută în toată pagina
                target_element = element.find_parent('html').find(id=target_id) if element.find_parent('html') else None
            
            if target_element:
                answer_text = target_element.get_text().strip()
        
        # Metodă 2: Caută în următorul sibling
        if not answer_text:
            next_sibling = element.find_next_sibling()
            if next_sibling:
                # Caută în mai multe tipuri de elemente
                for tag in ['div', 'p', 'section', 'article']:
                    if next_sibling.name == tag:
                        answer_text = next_sibling.get_text().strip()
                        break
                    # Caută și în copiii next_sibling
                    answer_elem = next_sibling.find(tag)
                    if answer_elem:
                        answer_text = answer_elem.get_text().strip()
                        break
        
        # Metodă 3: Caută în același container parent
        if not answer_text:
            parent = element.find_parent()
            if parent:
                # Caută toate paragrafele sau div-urile din parent
                content_elements = parent.find_all(['p', 'div', 'span'])
                for content_elem in content_elements:
                    content_text = content_elem.get_text().strip()
                    if (len(content_text) > 30 and 
                        content_text != question_text and
                        not any(word in content_text.lower() for word in ['ce', 'cum', 'care']) and
                        '?' not in content_text):
                        answer_text = content_text
                        break
        
        # Metodă 4: Caută în atributele elementului (uneori răspunsul e în title, data-content, etc.)
        if not answer_text:
            for attr in ['title', 'data-content', 'data-original-title', 'alt']:
                attr_value = element.get(attr, '')
                if attr_value and len(attr_value) > 20:
                    answer_text = attr_value
                    break
        
        if question_text and answer_text and len(answer_text) > 10:
            faq_item = {
                'question': question_text,
                'answer': answer_text[:500] + '...' if len(answer_text) > 500 else answer_text,
                'element_info': {
                    'tag': element.name,
                    'classes': element.get('class', []),
                    'id': element.get('id', ''),
                    'data_attributes': {k: v for k, v in element.attrs.items() if k.startswith('data-')}
                }
            }
            return faq_item
        
        return None

    def _extract_accordion_content(self, soup):
        """Extrage conținut din acordeoane"""
        accordion_content = []
        
        # Caută acordeoane Bootstrap și generice
        accordion_selectors = [
            '.accordion', '.accordion-group', '.panel-group',
            '.collapse', '.collapsible', '.expandable'
        ]
        
        for selector in accordion_selectors:
            accordions = soup.select(selector)
            
            for accordion in accordions:
                sections = accordion.find_all(['div', 'section'])
                
                for section in sections:
                    # Caută header/trigger
                    headers = section.find_all(['h1', 'h2', 'h3', 'h4', 'button', 'a'])
                    
                    for header in headers:
                        header_text = header.get_text().strip()
                        if len(header_text) > 10:
                            # Caută conținutul asociat
                            content_div = header.find_next_sibling(['div', 'p', 'section'])
                            if content_div:
                                content_text = content_div.get_text().strip()
                                if len(content_text) > 20:
                                    accordion_content.append({
                                        'header': header_text,
                                        'content': content_text[:400],
                                        'type': 'accordion'
                                    })
        
        return accordion_content[:10]

    def _extract_toggle_content(self, soup):
        """Extrage conținut din toggle/show-hide elements"""
        toggle_content = []
        
        # Caută elemente cu funcționalitate toggle
        toggle_indicators = ['show', 'hide', 'toggle', 'expand', 'collapse']
        
        for indicator in toggle_indicators:
            # Caută prin clase
            toggle_elements = soup.find_all(class_=re.compile(indicator, re.I))
            
            for element in toggle_elements:
                element_text = element.get_text().strip()
                if len(element_text) > 20:
                    # Încearcă să găsească conținutul asociat
                    associated_content = self._find_associated_content(element)
                    if associated_content:
                        toggle_content.append({
                            'trigger': element_text[:100],
                            'content': associated_content[:300],
                            'type': 'toggle'
                        })
        
        return toggle_content[:8]

    def _find_associated_content(self, element):
        """Găsește conținutul asociat cu un element trigger"""
        # Caută prin data-target
        target = element.get('data-target', '').replace('#', '')
        if target:
            target_elem = element.find_parent('html').find(id=target) if element.find_parent('html') else None
            if target_elem:
                return target_elem.get_text().strip()
        
        # Caută în next sibling
        next_elem = element.find_next_sibling()
        if next_elem:
            return next_elem.get_text().strip()
        
        # Caută în parent container
        parent = element.find_parent()
        if parent:
            siblings = parent.find_all(['div', 'p'])
            for sibling in siblings:
                if sibling != element:
                    text = sibling.get_text().strip()
                    if len(text) > 20:
                        return text
        
        return ''

    def _extract_hidden_content(self, soup):
        """Extrage conținut ascuns în elemente HTML"""
        hidden_content = []
        
        # Caută elemente cu display: none sau visibility: hidden
        hidden_elements = soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden', re.I))
        
        for hidden in hidden_elements:
            text = hidden.get_text().strip()
            if len(text) > 30:
                # Încearcă să găsească trigger-ul asociat
                hidden_id = hidden.get('id', '')
                if hidden_id:
                    triggers = soup.find_all(attrs={'data-target': f'#{hidden_id}'})
                    triggers.extend(soup.find_all(href=f'#{hidden_id}'))
                    
                    for trigger in triggers:
                        trigger_text = trigger.get_text().strip()
                        if len(trigger_text) > 10:
                            hidden_content.append({
                                'trigger': trigger_text,
                                'hidden_content': text[:400],
                                'type': 'hidden'
                            })
                            break
        
        return hidden_content[:8]

    def _combine_all_faqs(self, faq_data):
        """Combină toate FAQ-urile extrase"""
        combined_faqs = []
        
        # Adaugă FAQ-urile dropdown clasice
        combined_faqs.extend(faq_data['dropdown_faqs'])
        
        # Adaugă FAQ-urile specifice BikeStylish
        combined_faqs.extend(faq_data.get('bikestylish_faqs', []))
        
        # Adaugă FAQ-urile din taburi
        for tab in faq_data.get('tab_content', []):
            for faq in tab.get('faqs', []):
                combined_faqs.append({
                    'question': faq['question'],
                    'answer': faq['answer'],
                    'source_type': f'tab_{tab["tab_name"]}'
                })
            
            # Convertește caracteristicile din taburi în FAQ-uri
            for feature in tab.get('features', []):
                if feature['title'] and feature['description']:
                    # Creează întrebări din caracteristici
                    question = f"Ce este {feature['title']}?"
                    if '?' not in question:
                        question = f"Care sunt caracteristicile pentru {feature['title']}?"
                    
                    combined_faqs.append({
                        'question': question,
                        'answer': feature['description'],
                        'source_type': f'feature_{tab["tab_name"]}'
                    })
        
        # Convertește acordeoanele în format FAQ
        for accordion in faq_data['accordion_sections']:
            if '?' in accordion['header'] or any(word in accordion['header'].lower() for word in ['ce', 'cum', 'care']):
                combined_faqs.append({
                    'question': accordion['header'],
                    'answer': accordion['content'],
                    'source_type': 'accordion'
                })
        
        # Convertește toggle content în FAQ
        for toggle in faq_data['toggle_content']:
            if '?' in toggle['trigger']:
                combined_faqs.append({
                    'question': toggle['trigger'],
                    'answer': toggle['content'],
                    'source_type': 'toggle'
                })
        
        # Convertește hidden content în FAQ
        for hidden in faq_data['hidden_answers']:
            combined_faqs.append({
                'question': hidden['trigger'],
                'answer': hidden['hidden_content'],
                'source_type': 'hidden'
            })
        
        # Deduplică bazat pe întrebări similare
        unique_faqs = []
        seen_questions = set()
        
        for faq in combined_faqs:
            question_key = re.sub(r'[^\w\s]', '', faq['question'].lower())[:50]
            if question_key not in seen_questions:
                seen_questions.add(question_key)
                unique_faqs.append(faq)
        
        return unique_faqs[:12]  # Maxim 12 FAQ-uri unice

    def test_dropdown_extraction(self, category_id="ghidoane"):
        """Testează extragerea pentru o categorie"""
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
        logger.info(f"🧪 Testez extragerea FAQ dropdown pentru: {category_id}")
        logger.info(f"📍 URL: {url}")
        
        faq_data = self.extract_dropdown_faqs(url, category_id)
        
        if faq_data:
            logger.info(f"\n📊 REZULTATE EXTRAGERE FAQ DROPDOWN:")
            logger.info(f"📋 FAQ-uri dropdown clasice: {len(faq_data['dropdown_faqs'])}")
            logger.info(f"🚀 FAQ-uri BikeStylish specifice: {len(faq_data.get('bikestylish_faqs', []))}")
            logger.info(f"📑 Conținut din taburi: {len(faq_data.get('tab_content', []))}")
            logger.info(f"🎵 Secțiuni acordeon: {len(faq_data['accordion_sections'])}")
            logger.info(f"🔄 Toggle content: {len(faq_data['toggle_content'])}")
            logger.info(f"🔒 Conținut ascuns: {len(faq_data['hidden_answers'])}")
            logger.info(f"✅ Total FAQ-uri combinate: {len(faq_data['combined_faqs'])}")
            
            # Afișează detalii despre taburi
            if faq_data.get('tab_content'):
                logger.info(f"\n📑 DETALII TABURI:")
                for i, tab in enumerate(faq_data['tab_content'], 1):
                    features_count = len(tab.get('features', []))
                    faqs_count = len(tab.get('faqs', []))
                    lists_count = len(tab.get('lists', []))
                    logger.info(f"   {i}. Tab '{tab['tab_name']}' (ID: {tab['tab_id']})")
                    logger.info(f"      🔧 Caracteristici: {features_count}")
                    logger.info(f"      ❓ FAQ-uri: {faqs_count}")
                    logger.info(f"      📋 Liste: {lists_count}")
                    if tab.get('text_content'):
                        logger.info(f"      📝 Text: {tab['text_content'][:50]}...")
            
            # Afișează exemple
            if faq_data['combined_faqs']:
                logger.info(f"\n📋 EXEMPLE FAQ-URI DROPDOWN:")
                for i, faq in enumerate(faq_data['combined_faqs'][:3], 1):
                    source = faq.get('source_type', 'classic')
                    logger.info(f"   {i}. [{source.upper()}] Q: {faq['question'][:80]}...")
                    logger.info(f"      A: {faq['answer'][:100]}...")
            
            # Salvează în JSON
            if 'content_structure' not in test_category:
                test_category['content_structure'] = {}
            
            test_category['content_structure']['dropdown_faq_content'] = faq_data
            
            self.save_categories(data)
            logger.info(f"\n✅ FAQ-uri dropdown salvate pentru categoria {category_id}!")

    # Metode noi pentru extragerea conținutului identificat în template
    
    def _extract_page_title(self, soup):
        """Extrage titlul paginii"""
        title_elem = soup.find('title')
        if title_elem:
            return title_elem.get_text().strip()
        
        h1_elem = soup.find('h1')
        if h1_elem:
            return h1_elem.get_text().strip()
        
        return None

    def _extract_meta_description(self, soup):
        """Extrage meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        return None

    def _extract_jsonld_schemas(self, soup):
        """Extrage toate schema.org JSON-LD din pagină"""
        schemas = []
        
        # Caută toate script-urile JSON-LD
        jsonld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in jsonld_scripts:
            try:
                if script.string:
                    schema_data = json.loads(script.string)
                    schemas.append(schema_data)
            except (json.JSONDecodeError, TypeError):
                continue
        
        return schemas

    def _extract_breadcrumbs(self, soup):
        """Extrage breadcrumbs"""
        breadcrumbs = []
        
        # Caută breadcrumbs din JSON-LD
        schemas = self._extract_jsonld_schemas(soup)
        for schema in schemas:
            if isinstance(schema, dict) and schema.get('@type') == 'BreadcrumbList':
                items = schema.get('itemListElement', [])
                for item in items:
                    if isinstance(item, dict):
                        breadcrumbs.append({
                            'name': item.get('name', ''),
                            'url': item.get('item', ''),
                            'position': item.get('position', 0)
                        })
        
        # Caută și în HTML
        breadcrumb_nav = soup.find(['nav', 'ol', 'ul'], class_=re.compile(r'breadcrumb'))
        if breadcrumb_nav:
            links = breadcrumb_nav.find_all('a')
            for i, link in enumerate(links):
                breadcrumbs.append({
                    'name': link.get_text().strip(),
                    'url': link.get('href', ''),
                    'position': i + 1
                })
        
        return breadcrumbs

    def _extract_quick_stats(self, soup):
        """Extrage quick stats/statistici rapide"""
        stats = []
        
        # Caută div-uri cu clase relevante
        stat_containers = soup.find_all(['div'], class_=re.compile(r'stat|quick-stat|metric'))
        
        for container in stat_containers:
            stat_items = container.find_all(['div'], class_=re.compile(r'stat-item|metric-item'))
            
            for item in stat_items:
                number_elem = item.find(['div', 'span'], class_=re.compile(r'number|value|metric'))
                label_elem = item.find(['div', 'span'], class_=re.compile(r'label|title|name'))
                
                if number_elem and label_elem:
                    stats.append({
                        'value': number_elem.get_text().strip(),
                        'label': label_elem.get_text().strip()
                    })
        
        return stats

    def _extract_product_grid(self, soup):
        """Extrage grid-ul de produse/categorii"""
        products = []
        
        # Caută grid-uri
        grid_containers = soup.find_all(['div'], class_=re.compile(r'product-grid|grid|card-grid'))
        
        for grid in grid_containers:
            cards = grid.find_all(['div'], class_=re.compile(r'card|product|item'))
            
            for card in cards:
                title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                desc_elem = card.find('p')
                
                if title_elem:
                    product = {
                        'title': title_elem.get_text().strip(),
                        'description': desc_elem.get_text().strip() if desc_elem else ''
                    }
                    products.append(product)
        
        return products

    def _extract_decision_tree(self, soup):
        """Extrage arborele de decizie (IF-THEN logic)"""
        decisions = []
        
        # Caută div-uri cu clase decision
        decision_containers = soup.find_all(['div'], class_=re.compile(r'decision'))
        
        for container in decision_containers:
            paragraphs = container.find_all('p')
            
            for p in paragraphs:
                text = p.get_text().strip()
                if 'IF' in text and '→' in text:
                    decisions.append(text)
        
        return decisions

    def _extract_nlp_summaries(self, soup):
        """Extrage rezumatele NLP (scurte/medii)"""
        summaries = {}
        
        # Caută div-uri cu clase summary
        summary_containers = soup.find_all(['div'], class_=re.compile(r'summary|nlp-summary'))
        
        for container in summary_containers:
            # Caută summary-short
            short_elem = container.find(['div', 'p'], class_=re.compile(r'short'))
            if short_elem:
                summaries['short'] = short_elem.get_text().strip()
            
            # Caută summary-medium
            medium_elem = container.find(['div', 'p'], class_=re.compile(r'medium'))
            if medium_elem:
                summaries['medium'] = medium_elem.get_text().strip()
        
        return summaries

    def _extract_component_links(self, soup):
        """Extrage link-urile către componente complementare"""
        components = []
        
        # Caută div-uri cu clase component
        comp_containers = soup.find_all(['div'], class_=re.compile(r'component'))
        
        for container in comp_containers:
            links = container.find_all('a', class_=re.compile(r'component-link'))
            
            for link in links:
                components.append({
                    'name': link.get_text().strip(),
                    'url': link.get('href', '')
                })
        
        return components

    def _extract_cta_section(self, soup):
        """Extrage secțiunea CTA (Call to Action)"""
        cta_data = {}
        
        # Caută div-uri CTA
        cta_containers = soup.find_all(['div'], class_=re.compile(r'cta'))
        
        for container in cta_containers:
            title_elem = container.find(['h1', 'h2', 'h3'])
            if title_elem:
                cta_data['title'] = title_elem.get_text().strip()
            
            # Caută beneficii
            benefits_container = container.find(['div'], class_=re.compile(r'benefit'))
            if benefits_container:
                benefit_items = benefits_container.find_all(['div'])
                cta_data['benefits'] = [item.get_text().strip() for item in benefit_items if item.get_text().strip()]
        
        return cta_data

    def _extract_intro_content(self, soup):
        """Extrage conținutul intro"""
        intro_data = {}
        
        # Caută div-uri intro
        intro_containers = soup.find_all(['div'], class_=re.compile(r'intro'))
        
        for container in intro_containers:
            text_elem = container.find(['p'], class_=re.compile(r'intro-text'))
            if text_elem:
                intro_data['text'] = text_elem.get_text().strip()
        
        return intro_data

    def _extract_knowledge_tables(self, soup):
        """Extrage tabelele cu cunoștințe tehnice"""
        tables = []
        
        # Caută toate tabelele
        table_elements = soup.find_all('table')
        
        for table in table_elements:
            table_data = {
                'headers': [],
                'rows': []
            }
            
            # Extrage header-ele
            headers = table.find_all('th')
            table_data['headers'] = [th.get_text().strip() for th in headers]
            
            # Extrage rândurile
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = [cell.get_text().strip() for cell in cells]
                    table_data['rows'].append(row_data)
            
            if table_data['headers'] or table_data['rows']:
                tables.append(table_data)
        
        return tables

if __name__ == "__main__":
    extractor = DropdownFAQExtractor(
        r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    )
    
    print("🧪 Testez extragerea FAQ-urilor cu răspunsuri dropdown...")
    extractor.test_dropdown_extraction("ghidoane")
