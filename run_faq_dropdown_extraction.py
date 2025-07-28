#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pentru procesarea completă și comprehensivă a FAQ-urilor dropdown și conținutului structurat
din toate categoriile BikeStylish conform template-ului excategorie.txt
"""

import json
import time
from dropdown_faq_extractor import DropdownFAQExtractor
import logging

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('faq_comprehensive_extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchFAQProcessor:
    def __init__(self):
        self.extractor = DropdownFAQExtractor(
            r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
        )
        
    def process_all_categories_with_faqs(self):
        """Procesează toate categoriile care au potențial FAQ-uri dropdown"""
        data = self.extractor.load_categories()
        if not data:
            logger.error("❌ Nu s-au putut încărca categoriile!")
            return
        
        categories = data.get('categories', [])
        logger.info(f"🚀 Începem procesarea FAQ-urilor dropdown pentru {len(categories)} categorii...")
        
        processed_count = 0
        success_count = 0
        categories_with_faqs = []
        
        for i, category in enumerate(categories, 1):
            category_id = category.get('id', f'unknown_{i}')
            category_name = category.get('name', 'Unknown')
            category_url = category.get('url', '')
            
            logger.info(f"\n📍 [{i}/{len(categories)}] Procesez categoria: {category_name} (ID: {category_id})")
            
            try:
                # Extrage FAQ-urile dropdown
                faq_data = self.extractor.extract_dropdown_faqs(category_url, category_id)
                
                if faq_data:
                    # Calculează statistici
                    total_faqs = len(faq_data.get('combined_faqs', []))
                    total_tabs = len(faq_data.get('tab_content', []))
                    total_dropdown = len(faq_data.get('dropdown_faqs', []))
                    total_bikestylish = len(faq_data.get('bikestylish_faqs', []))
                    
                    # Salvează doar dacă are conținut util
                    if total_faqs > 0 or total_tabs > 0:
                        # Salvează în structura categoriei
                        if 'content_structure' not in category:
                            category['content_structure'] = {}
                        
                        category['content_structure']['dropdown_faq_content'] = faq_data
                        success_count += 1
                        
                        categories_with_faqs.append({
                            'id': category_id,
                            'name': category_name,
                            'total_faqs': total_faqs,
                            'total_tabs': total_tabs,
                            'dropdown_faqs': total_dropdown,
                            'bikestylish_faqs': total_bikestylish
                        })
                        
                        logger.info(f"✅ FAQ-uri salvate: {total_faqs} FAQ-uri, {total_tabs} taburi")
                    else:
                        logger.info(f"⚪ Categoria nu are FAQ-uri dropdown")
                
                processed_count += 1
                
                # Pauză între request-uri pentru a nu supraîncărca serverul
                if i % 10 == 0:
                    logger.info(f"⏸️  Pauză scurtă după {i} categorii...")
                    time.sleep(2)
                else:
                    time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"❌ Eroare la procesarea categoriei {category_id}: {e}")
                continue
        
        # Salvează toate modificările
        logger.info(f"\n💾 Salvez toate modificările...")
        if self.extractor.save_categories(data):
            logger.info(f"✅ Toate categoriile au fost salvate cu succes!")
        else:
            logger.error(f"❌ Eroare la salvarea categoriilor!")
        
        # Raport final
        logger.info(f"\n📊 RAPORT FINAL FAQ DROPDOWN:")
        logger.info(f"📋 Categorii procesate: {processed_count}/{len(categories)}")
        logger.info(f"✅ Categorii cu FAQ-uri: {success_count}")
        logger.info(f"📈 Rata de succes: {success_count/processed_count*100:.1f}%")
        
        logger.info(f"\n🏆 TOP CATEGORII CU CELE MAI MULTE FAQ-URI:")
        categories_with_faqs.sort(key=lambda x: x['total_faqs'], reverse=True)
        
        for i, cat in enumerate(categories_with_faqs[:10], 1):
            logger.info(f"   {i}. {cat['name']} - {cat['total_faqs']} FAQ-uri, {cat['total_tabs']} taburi")
        
        return {
            'processed': processed_count,
            'success': success_count,
            'categories_with_faqs': categories_with_faqs
        }

    def test_specific_categories(self, category_list=None):
        """Testează categorii specifice"""
        if not category_list:
            # Categorii cu potențial ridicat pentru FAQ-uri (ID-uri reale din JSON)
            category_list = [
                'ghidoane', 'mansoane', 'pedale-platforma', 'pedale-click', 'pedale-duble',
                'antifurturi', 'aparatori-noroi', 'suport-bidon-si-bidon', 'accesorii-bicicleta',
                'ghidoline', 'parti-ghidoane-si-barend-extensiighidon', 'borsete-sa',
                'transport-si-depozitare', 'reflectorizante', 'scaune-pentru-copii'
            ]
        
        logger.info(f"🧪 Testez {len(category_list)} categorii specifice...")
        
        results = []
        for category_id in category_list:
            logger.info(f"\n🔍 Testez categoria: {category_id}")
            faq_data = self.extractor.test_dropdown_extraction(category_id)
            
            if faq_data:
                total_faqs = len(faq_data.get('combined_faqs', []))
                total_tabs = len(faq_data.get('tab_content', []))
                
                results.append({
                    'category': category_id,
                    'faqs': total_faqs,
                    'tabs': total_tabs,
                    'status': 'success' if total_faqs > 0 or total_tabs > 0 else 'empty'
                })
            else:
                results.append({
                    'category': category_id,
                    'faqs': 0,
                    'tabs': 0,
                    'status': 'error'
                })
            
            time.sleep(1)  # Pauză între teste
        
        # Raport test
        logger.info(f"\n📊 RAPORT TEST CATEGORII SPECIFICE:")
        for result in results:
            status_emoji = "✅" if result['status'] == 'success' else "⚪" if result['status'] == 'empty' else "❌"
            logger.info(f"   {status_emoji} {result['category']}: {result['faqs']} FAQ-uri, {result['tabs']} taburi")
        
        return results

if __name__ == "__main__":
    processor = BatchFAQProcessor()
    
    print("🚀 Procesez FAQ-urile dropdown din BikeStylish...")
    print("Opțiuni:")
    print("1. Testează categorii specifice (mai rapid)")
    print("2. Procesează toate categoriile (mai lent)")
    
    choice = input("\nAlege opțiunea (1 sau 2): ").strip()
    
    if choice == "1":
        processor.test_specific_categories()
    elif choice == "2":
        processor.process_all_categories_with_faqs()
    else:
        print("🧪 Rullez testul pe categorii specifice...")
        processor.test_specific_categories()
