#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pentru combinarea finală a datelor FAQ dropdown extrase cu categoriile AI enhanced
Creează structura finală cu toate datele integrate
"""

import json
import time
from datetime import datetime
import logging

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('faq_integration_final.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FAQDataIntegrator:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        
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
    
    def integrate_faq_data(self):
        """Integrează toate datele FAQ dropdown cu categoriile AI enhanced"""
        logger.info("🚀 Începem integrarea finală a datelor FAQ dropdown...")
        
        data = self.load_categories()
        if not data:
            logger.error("❌ Nu s-au putut încărca categoriile")
            return False
        
        categories = data.get('categories', [])
        total_categories = len(categories)
        
        # Statistici
        categories_with_faq = 0
        categories_with_content = 0
        total_faqs = 0
        total_tabs = 0
        total_schemas = 0
        total_tables = 0
        
        enhanced_categories = []
        
        for i, category in enumerate(categories, 1):
            category_id = category.get('id', 'unknown')
            category_name = category.get('name', 'Unknown')
            
            logger.info(f"📍 [{i}/{total_categories}] Procesez categoria: {category_name} ({category_id})")
            
            # Verifică dacă categoria are dropdown_faq_content
            has_faq_content = (
                'content_structure' in category and 
                'dropdown_faq_content' in category.get('content_structure', {})
            )
            
            if has_faq_content:
                categories_with_content += 1
                faq_content = category['content_structure']['dropdown_faq_content']
                
                # Statistici pentru această categorie
                faqs_count = len(faq_content.get('combined_faqs', []))
                tabs_count = len(faq_content.get('tab_content', []))
                schemas_count = len(faq_content.get('jsonld_schemas', []))
                tables_count = len(faq_content.get('knowledge_tables', []))
                
                if faqs_count > 0:
                    categories_with_faq += 1
                    total_faqs += faqs_count
                    total_tabs += tabs_count
                    total_schemas += schemas_count
                    total_tables += tables_count
                    
                    logger.info(f"   ✅ {faqs_count} FAQ-uri, {tabs_count} taburi, {schemas_count} schemas, {tables_count} tabele")
                    
                    # Îmbunătățește categoria cu informații suplimentare
                    category = self._enhance_category_with_faq_data(category, faq_content)
                else:
                    logger.info(f"   ⚪ Categorie procesată dar fără FAQ-uri")
            else:
                logger.info(f"   ⚫ Categorie fără conținut FAQ dropdown")
            
            enhanced_categories.append(category)
        
        # Actualizează datele cu categoriile enhanced
        data['categories'] = enhanced_categories
        data['extraction_summary'] = {
            'extraction_completed': datetime.now().isoformat(),
            'total_categories': total_categories,
            'categories_processed': categories_with_content,
            'categories_with_faqs': categories_with_faq,
            'total_faqs_extracted': total_faqs,
            'total_tabs_processed': total_tabs,
            'total_schemas_found': total_schemas,
            'total_knowledge_tables': total_tables,
            'success_rate': f"{categories_with_faq/total_categories*100:.1f}%"
        }
        
        # Salvează rezultatul final
        if self.save_categories(data):
            logger.info(f"\n🎉 INTEGRARE FINALĂ COMPLETĂ!")
            logger.info(f"📊 STATISTICI FINALE:")
            logger.info(f"   📁 Total categorii: {total_categories}")
            logger.info(f"   ✅ Categorii procesate: {categories_with_content}")
            logger.info(f"   📋 Categorii cu FAQ-uri: {categories_with_faq}")
            logger.info(f"   🎯 Rata de succes: {categories_with_faq/total_categories*100:.1f}%")
            logger.info(f"   📋 Total FAQ-uri: {total_faqs}")
            logger.info(f"   📑 Total taburi: {total_tabs}")
            logger.info(f"   🎭 Total schemas: {total_schemas}")
            logger.info(f"   📊 Total tabele: {total_tables}")
            logger.info(f"\n💾 Datele finale au fost salvate în: {self.json_file_path}")
            return True
        else:
            logger.error("❌ Eroare la salvarea datelor finale")
            return False
    
    def _enhance_category_with_faq_data(self, category, faq_content):
        """Îmbunătățește categoria cu metadate din FAQ data"""
        
        # Adaugă metadate de conținut
        if 'content_metadata' not in category:
            category['content_metadata'] = {}
        
        # Informații despre FAQ-uri
        faqs = faq_content.get('combined_faqs', [])
        if faqs:
            category['content_metadata']['faq_summary'] = {
                'total_faqs': len(faqs),
                'faq_topics': [faq['question'][:50] + '...' for faq in faqs[:5]],
                'sources': list(set([faq.get('source_type', 'classic') for faq in faqs]))
            }
        
        # Informații despre taburi
        tabs = faq_content.get('tab_content', [])
        if tabs:
            category['content_metadata']['tab_summary'] = {
                'total_tabs': len(tabs),
                'tab_names': [tab['tab_name'] for tab in tabs],
                'total_features': sum(len(tab.get('features', [])) for tab in tabs)
            }
        
        # Informații despre schemas
        schemas = faq_content.get('jsonld_schemas', [])
        if schemas:
            schema_types = []
            for schema in schemas:
                if isinstance(schema, dict):
                    schema_type = schema.get('@type', 'Unknown')
                    if isinstance(schema_type, list):
                        schema_types.extend(schema_type)
                    else:
                        schema_types.append(schema_type)
            
            category['content_metadata']['schema_summary'] = {
                'total_schemas': len(schemas),
                'schema_types': list(set(schema_types))
            }
        
        # Informații despre pagină
        page_info = {}
        if faq_content.get('page_title'):
            page_info['title'] = faq_content['page_title']
        if faq_content.get('meta_description'):
            page_info['description'] = faq_content['meta_description']
        if faq_content.get('breadcrumbs'):
            page_info['breadcrumbs_count'] = len(faq_content['breadcrumbs'])
        
        if page_info:
            category['content_metadata']['page_info'] = page_info
        
        # Adaugă timestamp ultima actualizare
        category['last_updated'] = datetime.now().isoformat()
        
        return category
    
    def create_summary_report(self):
        """Creează un raport sumar cu rezultatele finale"""
        data = self.load_categories()
        if not data:
            return
        
        summary = data.get('extraction_summary', {})
        categories = data.get('categories', [])
        
        # Categorii cu cele mai multe FAQ-uri
        categories_with_faqs = []
        for cat in categories:
            if ('content_structure' in cat and 
                'dropdown_faq_content' in cat.get('content_structure', {})):
                faq_content = cat['content_structure']['dropdown_faq_content']
                faqs_count = len(faq_content.get('combined_faqs', []))
                if faqs_count > 0:
                    categories_with_faqs.append({
                        'name': cat.get('name', 'Unknown'),
                        'id': cat.get('id', 'unknown'),
                        'faqs_count': faqs_count,
                        'tabs_count': len(faq_content.get('tab_content', [])),
                        'url': cat.get('url', '')
                    })
        
        # Sortează după numărul de FAQ-uri
        categories_with_faqs.sort(key=lambda x: x['faqs_count'], reverse=True)
        
        # Creează raportul
        report = {
            'report_generated': datetime.now().isoformat(),
            'summary': summary,
            'top_categories_by_faqs': categories_with_faqs[:20],
            'categories_by_content_type': {
                'with_faqs': len([c for c in categories_with_faqs if c['faqs_count'] > 0]),
                'with_tabs': len([c for c in categories_with_faqs if c['tabs_count'] > 0]),
                'total_processed': len(categories_with_faqs)
            }
        }
        
        # Salvează raportul
        report_file = 'faq_extraction_final_report.json'
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"📊 Raport final salvat în: {report_file}")
        except Exception as e:
            logger.error(f"Eroare la salvarea raportului: {e}")

def main():
    """Funcția principală"""
    integrator = FAQDataIntegrator(
        r"data\categories_ai_enhanced.json"
    )
    
    print("🎯 Integrarea finală a datelor FAQ dropdown cu categoriile AI enhanced...")
    print("=" * 80)
    
    # Integrează datele
    success = integrator.integrate_faq_data()
    
    if success:
        print("\n📊 Generez raportul final...")
        integrator.create_summary_report()
        print("\n✅ Procesare completă! Toate datele au fost integrate cu succes.")
    else:
        print("\n❌ Erori în timpul integrării. Verifică log-urile pentru detalii.")

if __name__ == "__main__":
    main()
