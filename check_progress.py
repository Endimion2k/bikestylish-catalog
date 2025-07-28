#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def check_processing_progress():
    """Verifică progresul procesării FAQ-urilor dropdown"""
    try:
        with open('data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = data.get('categories', [])
        total_categories = len(categories)
        
        processed_categories = []
        for cat in categories:
            if 'content_structure' in cat and 'dropdown_faq_content' in cat.get('content_structure', {}):
                faq_content = cat['content_structure']['dropdown_faq_content']
                processed_categories.append({
                    'name': cat.get('name', 'N/A'),
                    'id': cat.get('id', 'N/A'),
                    'faqs': len(faq_content.get('combined_faqs', [])),
                    'tabs': len(faq_content.get('tab_content', [])),
                    'schemas': len(faq_content.get('jsonld_schemas', [])),
                    'tables': len(faq_content.get('knowledge_tables', []))
                })
        
        processed_count = len(processed_categories)
        
        print(f"📊 PROGRES PROCESARE FAQ DROPDOWN:")
        print(f"✅ {processed_count} / {total_categories} categorii procesate ({processed_count/total_categories*100:.1f}%)")
        print(f"\n🎯 TOP CATEGORII PROCESATE:")
        
        for i, cat in enumerate(processed_categories[:15], 1):
            print(f"   {i:2d}. {cat['name']} ({cat['id']})")
            print(f"       📋 {cat['faqs']} FAQ-uri, 📑 {cat['tabs']} taburi, 🎭 {cat['schemas']} schemas, 📊 {cat['tables']} tabele")
        
        if processed_count > 15:
            print(f"       ... și încă {processed_count - 15} categorii procesate")
        
        # Statistici generale
        total_faqs = sum(cat['faqs'] for cat in processed_categories)
        total_tabs = sum(cat['tabs'] for cat in processed_categories)
        total_schemas = sum(cat['schemas'] for cat in processed_categories)
        total_tables = sum(cat['tables'] for cat in processed_categories)
        
        print(f"\n📈 STATISTICI GENERALE:")
        print(f"📋 Total FAQ-uri extrase: {total_faqs}")
        print(f"📑 Total taburi procesate: {total_tabs}")
        print(f"🎭 Total JSON-LD schemas: {total_schemas}")
        print(f"📊 Total tabele cunoștințe: {total_tables}")
        
    except Exception as e:
        print(f"❌ Eroare la verificarea progresului: {e}")

if __name__ == "__main__":
    check_processing_progress()
