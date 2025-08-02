#!/usr/bin/env python3
"""
Script de verificare API BikeStylish
Testează toate endpoint-urile și raportează statusul
"""

import requests
import json
import time
from typing import Dict, List, Tuple
import sys

class APITester:
    def __init__(self, base_url: str = "https://endimion2k.github.io/bikestylish-catalog"):
        self.base_url = base_url.rstrip('/')
        self.results = {
            'products': {},
            'categories': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'errors': []
            }
        }
    
    def test_endpoint(self, url: str, endpoint_type: str, part_num: int) -> Tuple[bool, str, Dict]:
        """Testează un endpoint specific și returnează rezultatul"""
        try:
            print(f"Testing {endpoint_type} part {part_num:02d}...", end=" ")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Validări specifice
                    if endpoint_type == 'products':
                        if 'products' not in data:
                            return False, "Missing 'products' key", {}
                        if 'part_info' not in data:
                            return False, "Missing 'part_info' key", {}
                        products_count = len(data['products'])
                        if products_count == 0:
                            return False, "No products found", {}
                    else:  # categories
                        if 'categories' not in data:
                            return False, "Missing 'categories' key", {}
                        if 'part_info' not in data:
                            return False, "Missing 'part_info' key", {}
                        products_count = len(data['categories'])
                        if products_count == 0:
                            return False, "No categories found", {}
                    
                    print(f"✅ OK ({products_count} items)")
                    return True, "OK", data
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Error")
                    return False, f"JSON decode error: {e}", {}
            else:
                print(f"❌ HTTP {response.status_code}")
                return False, f"HTTP {response.status_code}", {}
                
        except requests.exceptions.Timeout:
            print("❌ Timeout")
            return False, "Request timeout", {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Error")
            return False, f"Request error: {e}", {}
    
    def test_products(self) -> None:
        """Testează toate endpoint-urile pentru produse"""
        print("\n🧪 Testing Products Endpoints (1-27):")
        print("-" * 50)
        
        for part in range(1, 28):
            part_str = f"{part:02d}"
            url = f"{self.base_url}/data/products_ai_enhanced_split/products_ai_enhanced_part_{part_str}.json"
            
            success, message, data = self.test_endpoint(url, 'products', part)
            
            self.results['products'][part] = {
                'url': url,
                'success': success,
                'message': message,
                'items_count': len(data.get('products', [])) if success else 0
            }
            
            self.results['summary']['total_tests'] += 1
            if success:
                self.results['summary']['passed'] += 1
            else:
                self.results['summary']['failed'] += 1
                self.results['summary']['errors'].append(f"Products part {part}: {message}")
            
            # Pauză scurtă pentru a nu supraîncărca serverul
            time.sleep(0.1)
    
    def test_categories(self) -> None:
        """Testează toate endpoint-urile pentru categorii"""
        print("\n🧪 Testing Categories Endpoints (1-26):")
        print("-" * 50)
        
        for part in range(1, 27):
            part_str = f"{part:02d}"
            url = f"{self.base_url}/data/categories_ai_enhanced_split/categories_ai_enhanced_part_{part_str}.json"
            
            success, message, data = self.test_endpoint(url, 'categories', part)
            
            self.results['categories'][part] = {
                'url': url,
                'success': success,
                'message': message,
                'items_count': len(data.get('categories', [])) if success else 0
            }
            
            self.results['summary']['total_tests'] += 1
            if success:
                self.results['summary']['passed'] += 1
            else:
                self.results['summary']['failed'] += 1
                self.results['summary']['errors'].append(f"Categories part {part}: {message}")
            
            time.sleep(0.1)
    
    def test_main_page(self) -> None:
        """Testează pagina principală API"""
        print("\n🧪 Testing Main API Page:")
        print("-" * 30)
        
        try:
            url = f"{self.base_url}/index.html"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print("✅ Main page OK")
                return True
            else:
                print(f"❌ Main page HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Main page error: {e}")
            return False
    
    def print_summary(self) -> None:
        """Afișează sumarele testelor"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        summary = self.results['summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        
        if summary['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED! API is fully functional!")
        else:
            print(f"\n⚠️  {summary['failed']} tests failed")
            print("\nErrors:")
            for error in summary['errors']:
                print(f"  • {error}")
        
        # Statistici produse
        total_products = sum(result['items_count'] for result in self.results['products'].values())
        products_parts_ok = sum(1 for result in self.results['products'].values() if result['success'])
        
        print(f"\n📦 Products: {total_products} total items in {products_parts_ok}/27 working parts")
        
        # Statistici categorii
        total_categories = sum(result['items_count'] for result in self.results['categories'].values())
        categories_parts_ok = sum(1 for result in self.results['categories'].values() if result['success'])
        
        print(f"📂 Categories: {total_categories} total items in {categories_parts_ok}/26 working parts")
        
        # Calculează success rate
        success_rate = (summary['passed'] / summary['total_tests']) * 100 if summary['total_tests'] > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print("🟢 API Status: EXCELLENT")
        elif success_rate >= 80:
            print("🟡 API Status: GOOD")
        elif success_rate >= 60:
            print("🟠 API Status: PARTIAL")
        else:
            print("🔴 API Status: CRITICAL")
    
    def save_results(self, filename: str = "api_test_results.json") -> None:
        """Salvează rezultatele în fișier JSON"""
        self.results['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to {filename}")
    
    def run_all_tests(self) -> bool:
        """Rulează toate testele"""
        print("🚀 Starting BikeStylish API Tests")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test pagina principală
        self.test_main_page()
        
        # Test produse
        self.test_products()
        
        # Test categorii
        self.test_categories()
        
        # Afișează sumarul
        self.print_summary()
        
        # Salvează rezultatele
        self.save_results()
        
        # Returnează True dacă toate testele au trecut
        return self.results['summary']['failed'] == 0

def main():
    """Funcția principală"""
    # Permite specificarea unui URL custom
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://endimion2k.github.io/bikestylish-catalog"
    
    tester = APITester(base_url)
    success = tester.run_all_tests()
    
    # Exit code pentru CI/CD
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
