#!/usr/bin/env python3
"""
Test script for BikeStylish scraper
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import BikeStylishScraper

def test_json_validation():
    """Test if the generated JSON is valid."""
    try:
        with open('../data/products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("✅ JSON structure is valid")
        
        # Check required fields
        required_fields = ['last_updated', 'total_products', 'categories', 'products']
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return False
        
        print(f"✅ Found {data['total_products']} products")
        print(f"✅ Found {len(data['categories'])} categories")
        return True
        
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return False

def test_scraper_basic():
    """Test basic scraper functionality."""
    try:
        scraper = BikeStylishScraper()
        
        # Test page fetching
        soup = scraper.get_page("https://bikestylish.ro")
        if soup:
            print("✅ Can fetch main page")
        else:
            print("❌ Cannot fetch main page")
            return False
        
        # Test price extraction
        test_prices = ["199,99 RON", "1.299 LEI", "€ 45.50"]
        for price_text in test_prices:
            price = scraper.extract_price(price_text)
            if price:
                print(f"✅ Extracted price {price} from '{price_text}'")
            else:
                print(f"⚠️ Could not extract price from '{price_text}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

def test_product_structure():
    """Test product data structure."""
    try:
        with open('../data/products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data['products']:
            print("❌ No products found")
            return False
        
        product = data['products'][0]
        required_product_fields = ['id', 'name', 'brand', 'category', 'price', 'currency']
        
        for field in required_product_fields:
            if field not in product:
                print(f"❌ Product missing required field: {field}")
                return False
        
        print("✅ Product structure is valid")
        print(f"✅ Sample product: {product['name']} - {product['price']} {product['currency']}")
        return True
        
    except Exception as e:
        print(f"❌ Product structure test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running BikeStylish Catalog Tests\n")
    
    tests = [
        ("JSON Validation", test_json_validation),
        ("Scraper Basic", test_scraper_basic),
        ("Product Structure", test_product_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
