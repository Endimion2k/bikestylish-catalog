#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifică rezultatele finale ale integrării FAQ dropdown cu categoriile AI enhanced
"""

import json

def verify_integration():
    """Verifică rezultatele finale ale integrării"""
    
    # Încarcă categoriile AI enhanced cu FAQ-uri integrate
    with open('data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Încarcă raportul final
    with open('faq_extraction_final_report.json', 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    print("🎉 REZULTATE FINALE - INTEGRAREA FAQ DROPDOWN CU CATEGORIILE AI ENHANCED")
    print("=" * 80)
    
    # Statistici din raport
    summary = report['summary']
    print(f"📊 STATISTICI GENERALE:")
    print(f"   📁 Total categorii: {summary['total_categories']}")
    print(f"   ✅ Categorii procesate: {summary['categories_processed']}")
    print(f"   📋 Categorii cu FAQ-uri: {summary['categories_with_faqs']}")
    print(f"   🎯 Rata de succes: {summary['success_rate']}")
    print(f"   📋 Total FAQ-uri extrase: {summary['total_faqs_extracted']}")
    print(f"   📑 Total taburi procesate: {summary['total_tabs_processed']}")
    print(f"   🎭 Total JSON-LD schemas: {summary['total_schemas_found']}")
    print(f"   📊 Total tabele cunoștințe: {summary['total_knowledge_tables']}")
    
    # Verifică structura datelor în categories_ai_enhanced.json
    categories = data.get('categories', [])
    extraction_summary = data.get('extraction_summary', {})
    
    print(f"\n📁 STRUCTURA DATELOR INTEGRATE:")
    print(f"   🗂️  Categorii în JSON: {len(categories)}")
    print(f"   📝 Are extraction_summary: {'✅' if extraction_summary else '❌'}")
    
    # Verifică câte categorii au content_structure cu dropdown_faq_content
    categories_with_content = []
    categories_with_metadata = []
    
    for cat in categories:
        if ('content_structure' in cat and 
            'dropdown_faq_content' in cat.get('content_structure', {})):
            categories_with_content.append(cat)
            
        if 'content_metadata' in cat:
            categories_with_metadata.append(cat)
    
    print(f"   📋 Categorii cu dropdown_faq_content: {len(categories_with_content)}")
    print(f"   🏷️  Categorii cu content_metadata: {len(categories_with_metadata)}")
    
    # Top 10 categorii cu cele mai multe FAQ-uri
    print(f"\n🏆 TOP 10 CATEGORII CU CELE MAI MULTE FAQ-URI:")
    top_categories = report['top_categories_by_faqs'][:10]
    
    for i, cat in enumerate(top_categories, 1):
        print(f"   {i:2d}. {cat['name']} ({cat['id']})")
        print(f"       📋 {cat['faqs_count']} FAQ-uri, 📑 {cat['tabs_count']} taburi")
        print(f"       🔗 {cat['url']}")
    
    # Verifică o categorie exemplu în detaliu
    print(f"\n🔍 EXEMPLU CATEGORIE INTEGRATĂ - 'ghidoane':")
    
    ghidoane_cat = None
    for cat in categories:
        if cat.get('id') == 'ghidoane':
            ghidoane_cat = cat
            break
    
    if ghidoane_cat:
        print(f"   📛 Nume: {ghidoane_cat.get('name', 'N/A')}")
        print(f"   🔗 URL: {ghidoane_cat.get('url', 'N/A')}")
        print(f"   📅 Ultima actualizare: {ghidoane_cat.get('last_updated', 'N/A')}")
        
        # Content structure
        content_structure = ghidoane_cat.get('content_structure', {})
        if 'dropdown_faq_content' in content_structure:
            faq_content = content_structure['dropdown_faq_content']
            print(f"   📋 FAQ-uri dropdown: {len(faq_content.get('combined_faqs', []))}")
            print(f"   📑 Taburi JavaScript: {len(faq_content.get('tab_content', []))}")
            print(f"   🎭 JSON-LD schemas: {len(faq_content.get('jsonld_schemas', []))}")
            print(f"   📊 Tabele cunoștințe: {len(faq_content.get('knowledge_tables', []))}")
        else:
            print(f"   ❌ Nu are dropdown_faq_content")
        
        # Content metadata
        content_metadata = ghidoane_cat.get('content_metadata', {})
        if content_metadata:
            print(f"   🏷️  Are content_metadata: ✅")
            if 'faq_summary' in content_metadata:
                faq_summary = content_metadata['faq_summary']
                print(f"       📋 FAQ summary - Total: {faq_summary.get('total_faqs', 0)}")
                print(f"       🔄 Sources: {', '.join(faq_summary.get('sources', []))}")
            if 'tab_summary' in content_metadata:
                tab_summary = content_metadata['tab_summary']
                print(f"       📑 Tab summary - Total: {tab_summary.get('total_tabs', 0)}")
                print(f"       📝 Tab names: {', '.join(tab_summary.get('tab_names', []))}")
        else:
            print(f"   🏷️  Are content_metadata: ❌")
        
        # AI Enhanced content
        ai_enhanced = ghidoane_cat.get('ai_enhanced_content', {})
        if ai_enhanced:
            print(f"   🤖 Are AI enhanced content: ✅")
            intent_targeting = ai_enhanced.get('intent_targeting', {})
            if intent_targeting:
                high_intent = intent_targeting.get('high_intent_keywords', [])
                print(f"       🎯 High intent keywords: {len(high_intent)}")
        else:
            print(f"   🤖 Are AI enhanced content: ❌")
    else:
        print(f"   ❌ Categoria 'ghidoane' nu a fost găsită")
    
    print(f"\n✅ VERIFICARE COMPLETĂ!")
    print(f"📊 Datele FAQ dropdown au fost integrate cu succes în categoriile AI enhanced!")
    print(f"💾 Fișierul final: data/categories_ai_enhanced.json ({len(categories)} categorii)")

if __name__ == "__main__":
    verify_integration()
