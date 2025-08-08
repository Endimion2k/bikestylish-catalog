#!/usr/bin/env python3
"""
Test API Endpoints - Verificare funcționalitate
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_endpoint(url, description):
    """Testează un endpoint"""
    try:
        print(f"🔍 {description}...")
        response = requests.get(f"{API_BASE}{url}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Analizează răspunsul
            if 'results' in data:
                count = len(data['results'])
                print(f"   ✅ {count} rezultate găsite")
                if count > 0:
                    first_item = data['results'][0]
                    name = first_item.get('name', 'N/A')[:50]
                    price = first_item.get('price', 'N/A')
                    print(f"   📦 Primul produs: {name}... ({price} RON)")
                    
            elif 'total_products' in data:
                print(f"   ✅ {data['total_products']} produse disponibile")
                
            elif 'total_handlebars' in data:
                total = data['total_handlebars']
                by_type = data.get('by_type', {})
                print(f"   ✅ {total} ghidoane găsite")
                for type_name, items in by_type.items():
                    if items:
                        print(f"      • {type_name}: {len(items)} produse")
                        
            elif 'categories' in data:
                print(f"   ✅ {len(data['categories'])} categorii")
                
            elif 'brands' in data:
                print(f"   ✅ {len(data['brands'])} branduri")
                
            else:
                print(f"   ✅ OK ({response.status_code})")
                
        else:
            print(f"   ❌ Eroare HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Nu pot conecta la server")
        print(f"      Asigură-te că serverul rulează pe {API_BASE}")
        return False
    except Exception as e:
        print(f"   ❌ Eroare: {e}")
        return False
    
    return True

def main():
    print("🧪 BikeStylish API - Test Suite")
    print("=" * 40)
    
    # Lista de teste
    tests = [
        ("/", "Info API"),
        ("/api/stats", "Statistici generale"),
        ("/api/categories", "Lista categoriilor"),
        ("/api/brands", "Lista brandurilor"),
        ("/api/products?limit=5", "Primele 5 produse"),
        ("/api/search?q=ghidon&limit=5", "Căutare 'ghidon' (5 rezultate)"),
        ("/api/search?q=SHIMANO&limit=3", "Căutare 'SHIMANO' (3 rezultate)"),
        ("/api/search?category=accesorii&limit=5", "Categoria 'accesorii' (5 rezultate)"),
        ("/api/search?min_price=100&max_price=200&limit=5", "Prețuri 100-200 RON (5 rezultate)"),
        ("/api/search?availability=in_stock&limit=5", "Produse în stoc (5 rezultate)"),
        ("/api/handlebars?limit=10", "Ghidoane și componente (10 rezultate)")
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    # Rulează testele
    for url, description in tests:
        if test_endpoint(url, description):
            success_count += 1
        time.sleep(0.5)  # Pauză scurtă între teste
    
    # Rezultate finale
    print("\n" + "=" * 40)
    print(f"📊 Rezultate finale: {success_count}/{total_tests} teste reușite")
    
    if success_count == total_tests:
        print("🎉 Toate testele au trecut! API-ul funcționează perfect!")
        print(f"🌐 Documentație: {API_BASE}/docs")
        print(f"🔍 Test manual: {API_BASE}/api/search?q=ghidon")
    else:
        failed = total_tests - success_count
        print(f"⚠️  {failed} teste eșuate")
        if success_count == 0:
            print("❌ Serverul nu pare să ruleze")
            print("🚀 Pornește serverul cu: python quick_start.py")
        else:
            print("🔧 Unele endpoint-uri au probleme")
    
    print("\n💡 Pentru a rula din nou testele: python test_endpoints.py")

if __name__ == "__main__":
    main()
