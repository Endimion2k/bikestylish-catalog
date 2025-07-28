#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pentru combinarea automată a datelor dropdown FAQ extrase cu categoriile AI enhanced
Monitorizează procesarea și combină rezultatele când extracția este completă
"""

import json
import time
import os
from datetime import datetime
import shutil

class FAQDataCombiner:
    def __init__(self):
        self.enhanced_file = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
        self.backup_dir = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\backups"
        
        # Asigură-te că există directorul de backup
        os.makedirs(self.backup_dir, exist_ok=True)

    def wait_for_extraction_completion(self):
        """Așteaptă să se termine extracția și monitorizează progresul"""
        print("🔄 Monitorizez progresul extracției FAQ dropdown...")
        
        last_count = 0
        no_change_count = 0
        
        while True:
            try:
                with open(self.enhanced_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                categories = data.get('categories', [])
                total_categories = len(categories)
                
                processed_count = sum(1 for cat in categories 
                                    if 'content_structure' in cat 
                                    and 'dropdown_faq_content' in cat.get('content_structure', {}))
                
                # Calculează categorii cu conținut real (nu goale)
                categories_with_content = 0
                total_faqs = 0
                total_tabs = 0
                
                for cat in categories:
                    if 'content_structure' in cat and 'dropdown_faq_content' in cat.get('content_structure', {}):
                        faq_content = cat['content_structure']['dropdown_faq_content']
                        faqs = len(faq_content.get('combined_faqs', []))
                        tabs = len(faq_content.get('tab_content', []))
                        
                        if faqs > 0 or tabs > 0:
                            categories_with_content += 1
                        
                        total_faqs += faqs
                        total_tabs += tabs
                
                percentage = (processed_count / total_categories) * 100
                
                print(f"📊 Progres: {processed_count}/{total_categories} ({percentage:.1f}%) | "
                      f"🎯 Cu conținut: {categories_with_content} | "
                      f"📋 FAQ-uri: {total_faqs} | "
                      f"📑 Taburi: {total_tabs}")
                
                # Verifică dacă procesarea s-a terminat
                if processed_count == total_categories:
                    print(f"✅ Extracția completă! Toate {total_categories} categorii procesate.")
                    return True
                
                # Verifică dacă nu mai sunt schimbări (posibil terminată)
                if processed_count == last_count:
                    no_change_count += 1
                    if no_change_count >= 10:  # 5 minute fără schimbări
                        print(f"⏸️ Nu mai sunt schimbări de 5 minute. Probabil extracția s-a terminat.")
                        print(f"📊 Status final: {processed_count}/{total_categories} categorii procesate")
                        return True
                else:
                    no_change_count = 0
                    last_count = processed_count
                
                time.sleep(30)  # Verifică la fiecare 30 secunde
                
            except Exception as e:
                print(f"❌ Eroare la monitorizare: {e}")
                time.sleep(30)

    def create_backup(self):
        """Creează backup înainte de combinare"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(self.backup_dir, f"categories_ai_enhanced_backup_{timestamp}.json")
        
        try:
            shutil.copy2(self.enhanced_file, backup_file)
            print(f"💾 Backup creat: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"❌ Eroare la crearea backup-ului: {e}")
            return None

    def combine_faq_data_with_ai_enhanced(self):
        """Combină datele FAQ extrase cu categoriile AI enhanced"""
        print("🔄 Încep combinarea datelor FAQ cu categoriile AI enhanced...")
        
        # Creează backup
        backup_file = self.create_backup()
        if not backup_file:
            print("❌ Nu s-a putut crea backup. Opresc procesul.")
            return False
        
        try:
            # Încarcă datele existente
            with open(self.enhanced_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            categories = data.get('categories', [])
            combined_count = 0
            enhanced_count = 0
            
            print(f"📂 Procesez {len(categories)} categorii...")
            
            for category in categories:
                category_id = category.get('id', '')
                category_name = category.get('name', '')
                
                # Verifică dacă categoria are date FAQ extrase
                if ('content_structure' in category and 
                    'dropdown_faq_content' in category.get('content_structure', {})):
                    
                    faq_content = category['content_structure']['dropdown_faq_content']
                    
                    # Îmbunătățește categoria cu datele FAQ
                    enhanced_category = self.enhance_category_with_faq_data(category, faq_content)
                    
                    if enhanced_category:
                        # Înlocuiește categoria originală
                        for i, cat in enumerate(data['categories']):
                            if cat.get('id') == category_id:
                                data['categories'][i] = enhanced_category
                                break
                        
                        enhanced_count += 1
                        print(f"✅ {enhanced_count:3d}. {category_name} ({category_id}) - îmbunătățit cu FAQ dropdown")
                    
                    combined_count += 1
            
            # Adaugă metadata despre combinare
            data['faq_combination_metadata'] = {
                'combination_timestamp': datetime.now().isoformat(),
                'total_categories_processed': len(categories),
                'categories_with_faq_data': combined_count,
                'categories_enhanced': enhanced_count,
                'backup_file': backup_file,
                'extraction_method': 'comprehensive_dropdown_faq_extraction'
            }
            
            # Salvează rezultatul combinat
            with open(self.enhanced_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n🎉 COMBINARE COMPLETĂ!")
            print(f"📊 Total categorii: {len(categories)}")
            print(f"📋 Cu date FAQ: {combined_count}")
            print(f"✨ Îmbunătățite: {enhanced_count}")
            print(f"💾 Backup salvat: {os.path.basename(backup_file)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Eroare la combinarea datelor: {e}")
            # Încearcă să restaureze backup-ul
            if backup_file and os.path.exists(backup_file):
                try:
                    shutil.copy2(backup_file, self.enhanced_file)
                    print(f"🔄 Backup restaurat din cauza erorii")
                except Exception as restore_error:
                    print(f"❌ Nu s-a putut restaura backup-ul: {restore_error}")
            return False

    def enhance_category_with_faq_data(self, category, faq_content):
        """Îmbunătățește o categorie cu datele FAQ extrase"""
        try:
            enhanced_category = category.copy()
            
            # Adaugă sau îmbunătățește secțiunea content_structure
            if 'content_structure' not in enhanced_category:
                enhanced_category['content_structure'] = {}
            
            # Combină FAQ-urile în formatul pentru AI enhanced
            if faq_content.get('combined_faqs'):
                enhanced_category['content_structure']['enhanced_faqs'] = []
                
                for faq in faq_content['combined_faqs']:
                    enhanced_faq = {
                        'question': faq.get('question', ''),
                        'answer': faq.get('answer', ''),
                        'source_type': faq.get('source_type', 'dropdown'),
                        'relevance_score': 0.9  # Score înalt pentru FAQ-uri dropdown
                    }
                    enhanced_category['content_structure']['enhanced_faqs'].append(enhanced_faq)
            
            # Adaugă informații despre taburi ca knowledge base
            if faq_content.get('tab_content'):
                enhanced_category['content_structure']['interactive_tabs'] = []
                
                for tab in faq_content['tab_content']:
                    enhanced_tab = {
                        'tab_name': tab.get('tab_name', ''),
                        'tab_id': tab.get('tab_id', ''),
                        'features_count': len(tab.get('features', [])),
                        'content_summary': tab.get('text_content', '')[:200],
                        'features': tab.get('features', []),
                        'lists': tab.get('lists', [])
                    }
                    enhanced_category['content_structure']['interactive_tabs'].append(enhanced_tab)
            
            # Adaugă metadata tehnice
            if faq_content.get('knowledge_tables'):
                enhanced_category['content_structure']['technical_specifications'] = faq_content['knowledge_tables']
            
            # Adaugă schema.org data pentru SEO
            if faq_content.get('jsonld_schemas'):
                enhanced_category['content_structure']['structured_data'] = {
                    'schemas_count': len(faq_content['jsonld_schemas']),
                    'schema_types': [schema.get('@type', 'Unknown') for schema in faq_content['jsonld_schemas'] if isinstance(schema, dict)],
                    'faq_schemas': [schema for schema in faq_content['jsonld_schemas'] if isinstance(schema, dict) and schema.get('@type') == 'FAQPage']
                }
            
            # Păstrează datele originale complete
            enhanced_category['content_structure']['dropdown_faq_content'] = faq_content
            
            # Adaugă scorul de completitudine
            completeness_score = self.calculate_completeness_score(faq_content)
            enhanced_category['content_structure']['completeness_score'] = completeness_score
            
            return enhanced_category
            
        except Exception as e:
            print(f"❌ Eroare la îmbunătățirea categoriei {category.get('id', 'unknown')}: {e}")
            return None

    def calculate_completeness_score(self, faq_content):
        """Calculează scorul de completitudine pentru o categorie"""
        score = 0.0
        max_score = 10.0
        
        # FAQ-uri (40% din scor)
        faqs_count = len(faq_content.get('combined_faqs', []))
        if faqs_count > 0:
            score += min(4.0, faqs_count * 0.4)
        
        # Taburi interactive (25% din scor)
        tabs_count = len(faq_content.get('tab_content', []))
        if tabs_count > 0:
            score += min(2.5, tabs_count * 0.6)
        
        # Schema.org data (15% din scor)
        schemas_count = len(faq_content.get('jsonld_schemas', []))
        if schemas_count > 0:
            score += min(1.5, schemas_count * 0.2)
        
        # Tabele cunoștințe (10% din scor)
        tables_count = len(faq_content.get('knowledge_tables', []))
        if tables_count > 0:
            score += min(1.0, tables_count * 0.5)
        
        # Conținut structurat (10% din scor)
        if faq_content.get('breadcrumbs') or faq_content.get('quick_stats'):
            score += 1.0
        
        return round((score / max_score) * 100, 1)

    def run_monitoring_and_combination(self):
        """Rulează monitorizarea și combinarea automată"""
        print("🚀 Sistem de monitorizare și combinare FAQ dropdown → AI enhanced")
        print("=" * 70)
        
        # Așteaptă ca extracția să se termine
        print("⏳ Aștept finalizarea extracției...")
        extraction_completed = self.wait_for_extraction_completion()
        
        if extraction_completed:
            print("\n🔄 Încep combinarea datelor...")
            success = self.combine_faq_data_with_ai_enhanced()
            
            if success:
                print("\n🎉 SUCCES! Datele FAQ dropdown au fost combinate cu categoriile AI enhanced!")
                
                # Afișează un raport final
                self.generate_final_report()
            else:
                print("\n❌ Combinarea a eșuat. Verifică log-urile pentru detalii.")
        else:
            print("\n⏸️ Extracția nu s-a finalizat complet. Încerc să combin datele disponibile...")
            self.combine_faq_data_with_ai_enhanced()

    def generate_final_report(self):
        """Generează un raport final cu statistici"""
        try:
            with open(self.enhanced_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            categories = data.get('categories', [])
            metadata = data.get('faq_combination_metadata', {})
            
            print("\n📊 RAPORT FINAL COMBINARE:")
            print("=" * 50)
            print(f"📅 Data combinării: {metadata.get('combination_timestamp', 'N/A')}")
            print(f"📂 Total categorii: {len(categories)}")
            print(f"📋 Cu date FAQ: {metadata.get('categories_with_faq_data', 0)}")
            print(f"✨ Îmbunătățite: {metadata.get('categories_enhanced', 0)}")
            
            # Statistici detaliate
            total_faqs = 0
            total_tabs = 0
            total_schemas = 0
            avg_completeness = 0
            
            categories_with_data = 0
            
            for cat in categories:
                if ('content_structure' in cat and 
                    'dropdown_faq_content' in cat.get('content_structure', {})):
                    
                    faq_content = cat['content_structure']['dropdown_faq_content']
                    total_faqs += len(faq_content.get('combined_faqs', []))
                    total_tabs += len(faq_content.get('tab_content', []))
                    total_schemas += len(faq_content.get('jsonld_schemas', []))
                    
                    completeness = cat.get('content_structure', {}).get('completeness_score', 0)
                    if completeness > 0:
                        avg_completeness += completeness
                        categories_with_data += 1
            
            if categories_with_data > 0:
                avg_completeness = avg_completeness / categories_with_data
            
            print(f"\n📈 STATISTICI CONȚINUT:")
            print(f"📋 Total FAQ-uri extrase: {total_faqs}")
            print(f"📑 Total taburi procesate: {total_tabs}")
            print(f"🎭 Total schema.org: {total_schemas}")
            print(f"📊 Scor mediu completitudine: {avg_completeness:.1f}%")
            
            print(f"\n💾 Backup salvat: {os.path.basename(metadata.get('backup_file', 'N/A'))}")
            print("\n✅ Categoriile AI enhanced sunt acum îmbunătățite cu date FAQ dropdown!")
            
        except Exception as e:
            print(f"❌ Eroare la generarea raportului: {e}")

if __name__ == "__main__":
    combiner = FAQDataCombiner()
    combiner.run_monitoring_and_combination()
