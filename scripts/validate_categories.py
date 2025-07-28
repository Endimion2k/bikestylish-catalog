#!/usr/bin/env python3
"""
Final validation of category integration
"""

import json

def validate_category_integration():
    """Validate that categories are properly integrated."""
    
    print("🔍 Validating category integration...")
    
    # Load all data files
    with open('../data/categories_detailed.json', 'r', encoding='utf-8') as f:
        categories_data = json.load(f)
    
    with open('../data/products_ai_enhanced.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Validation checks
    checks_passed = 0
    total_checks = 8
    
    # Check 1: Categories file exists and has data
    if categories_data['total_categories'] == 101:
        print("✅ Categories file contains 101 categories")
        checks_passed += 1
    else:
        print(f"❌ Expected 101 categories, found {categories_data['total_categories']}")
    
    # Check 2: Catalog has categories_detailed section
    if 'categories_detailed' in catalog:
        print("✅ Main catalog contains categories_detailed section")
        checks_passed += 1
    else:
        print("❌ Main catalog missing categories_detailed section")
    
    # Check 3: Category types are correctly classified
    expected_types = {'accesorii', 'copii', 'general', 'e-bike', 'piese', 'scule', 'echipament'}
    actual_types = set(categories_data['mappings']['type_groups'].keys())
    
    if expected_types.issubset(actual_types):
        print(f"✅ All expected category types present: {len(actual_types)} types")
        checks_passed += 1
    else:
        missing = expected_types - actual_types
        print(f"❌ Missing category types: {missing}")
    
    # Check 4: URL mappings exist
    url_mappings = categories_data['mappings']['url_to_category']
    if len(url_mappings) == 101:
        print(f"✅ All {len(url_mappings)} categories have URL mappings")
        checks_passed += 1
    else:
        print(f"❌ Expected 101 URL mappings, found {len(url_mappings)}")
    
    # Check 5: Search terms generated
    search_terms = categories_data['mappings']['search_terms']
    if len(search_terms) == 101:
        print(f"✅ Search terms generated for all {len(search_terms)} categories")
        checks_passed += 1
    else:
        print(f"❌ Search terms missing for some categories")
    
    # Check 6: Hierarchical structure exists
    hierarchy = categories_data['hierarchy']
    main_cats = len(hierarchy['main_categories'])
    if main_cats > 0:
        print(f"✅ Hierarchical structure created with {main_cats} main categories")
        checks_passed += 1
    else:
        print("❌ No main categories found in hierarchy")
    
    # Check 7: AI optimization includes category features
    if 'ai_optimization' in catalog and 'category_features' in catalog['ai_optimization']:
        print("✅ AI optimization includes category features")
        checks_passed += 1
    else:
        print("❌ AI optimization missing category features")
    
    # Check 8: README file exists
    try:
        with open('../README.md', 'r', encoding='utf-8') as f:
            readme_content = f.read()
        if 'Category Structure' in readme_content and '101 structured categories' in readme_content:
            print("✅ README updated with category information")
            checks_passed += 1
        else:
            print("❌ README missing category information")
    except:
        print("❌ README file not found or not readable")
    
    # Final validation result
    print(f"\n📊 Validation Results: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 ALL VALIDATIONS PASSED! Categories successfully integrated.")
        
        # Show detailed statistics
        print(f"\n📋 Final Category Statistics:")
        print(f"   Total categories: {categories_data['total_categories']}")
        print(f"   Category types: {len(categories_data['mappings']['type_groups'])}")
        print(f"   Main categories: {len(hierarchy['main_categories'])}")
        print(f"   URL mappings: {len(url_mappings)}")
        print(f"   Search terms: {len(search_terms)}")
        
        # Show category breakdown
        print(f"\n🗂️ Category Breakdown:")
        for cat_type, cats in categories_data['mappings']['type_groups'].items():
            print(f"   {cat_type.upper()}: {len(cats)} categories")
        
        print(f"\n✅ Repository is ready for GitHub upload with complete category structure!")
        
    else:
        print(f"⚠️ {total_checks - checks_passed} validations failed. Please review and fix issues.")
    
    return checks_passed == total_checks

if __name__ == "__main__":
    validate_category_integration()
