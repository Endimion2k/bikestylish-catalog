#!/usr/bin/env python3
"""
Script de pornire pentru serverele BikeStylish API
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def install_requirements(requirements_file):
    """Instalează dependențele"""
    if not os.path.exists(requirements_file):
        print(f"❌ Nu s-a găsit {requirements_file}")
        return False
    
    print(f"📦 Instalez dependențele din {requirements_file}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✅ Dependențe instalate cu succes!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Eroare la instalarea dependențelor: {e}")
        return False

def start_flask_server():
    """Pornește serverul Flask"""
    print("\n🚀 Pornesc serverul Flask...")
    print("📋 Endpoint-uri disponibile:")
    print("   • http://localhost:5000/ - Info API")
    print("   • http://localhost:5000/api/products - Lista produse")
    print("   • http://localhost:5000/api/search?q=ghidon - Căutare")
    print("   • http://localhost:5000/api/handlebars - Ghidoane")
    print("   • http://localhost:5000/api/stats - Statistici")
    print("\n💡 Pentru a opri serverul, apasă Ctrl+C")
    print("=" * 50)
    
    # Deschide browserul după 2 secunde
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:5000')
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        # Pornește serverul
        subprocess.call([sys.executable, "api_server.py"])
    except KeyboardInterrupt:
        print("\n\n✅ Server oprit cu succes!")
        print("👋 Mulțumesc că ai folosit BikeStylish API!")
    except Exception as e:
        print(f"\n❌ Eroare la pornirea serverului: {e}")
        print("🔧 Încearcă să rulezi manual: python api_server.py")

def start_fastapi_server():
    """Pornește serverul FastAPI"""
    print("\n🚀 Pornesc serverul FastAPI...")
    print("📋 Endpoint-uri disponibile:")
    print("   • http://localhost:8000/ - Info API")
    print("   • http://localhost:8000/docs - Documentație Swagger")
    print("   • http://localhost:8000/api/products - Lista produse")
    print("   • http://localhost:8000/api/search?q=ghidon - Căutare")
    print("   • http://localhost:8000/api/handlebars - Ghidoane")
    print("\n💡 Pentru a opri serverul, apasă Ctrl+C")
    print("=" * 50)
    
    # Deschide browserul
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:8000/docs')
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        # Pornește serverul
        subprocess.call([sys.executable, "fastapi_server.py"])
    except KeyboardInterrupt:
        print("\n\n✅ Server oprit cu succes!")
        print("👋 Mulțumesc că ai folosit BikeStylish API!")
    except Exception as e:
        print(f"\n❌ Eroare la pornirea serverului: {e}")
        print("🔧 Încearcă să rulezi manual: python fastapi_server.py")

def open_test_client():
    """Deschide clientul de test HTML"""
    client_path = Path("test_client.html").absolute()
    if client_path.exists():
        print(f"🌐 Deschid clientul de test: {client_path}")
        webbrowser.open(f"file://{client_path}")
    else:
        print("❌ Nu s-a găsit test_client.html")

def test_api_quick():
    """Test rapid al API-ului"""
    print("\n🧪 Test rapid BikeStylish API")
    print("=" * 40)
    
    if not install_requirements("requirements_fastapi.txt"):
        return
    
    print("🚀 Pornesc serverul FastAPI pentru test...")
    
    # Pornește serverul în background
    def start_server():
        subprocess.Popen([sys.executable, "fastapi_server.py"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
    
    import threading
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Așteaptă să pornească serverul
    print("⏳ Aștept 5 secunde să pornească serverul...")
    time.sleep(5)
    
    # Testează endpoint-urile
    test_urls = [
        ("http://localhost:8000/", "Info API"),
        ("http://localhost:8000/api/stats", "Statistici"),
        ("http://localhost:8000/api/handlebars?limit=5", "Ghidoane (5 rezultate)"),
        ("http://localhost:8000/api/search?q=ghidon&limit=3", "Căutare ghidon (3 rezultate)")
    ]
    
    try:
        import requests
        
        for url, description in test_urls:
            try:
                print(f"\n🔍 Testez: {description}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data:
                        print(f"   ✅ {len(data['results'])} rezultate găsite")
                    elif 'total_products' in data:
                        print(f"   ✅ {data['total_products']} produse total")
                    elif 'total_handlebars' in data:
                        print(f"   ✅ {data['total_handlebars']} ghidoane găsite")
                    else:
                        print(f"   ✅ OK - {response.status_code}")
                else:
                    print(f"   ❌ Error {response.status_code}")
            except Exception as e:
                print(f"   ❌ Eroare: {e}")
        
        print(f"\n🌐 Documentație Swagger: http://localhost:8000/docs")
        print("💡 Serverul rulează în background. Pentru a-l opri, închide terminalul.")
        
        # Deschide browserul
        webbrowser.open('http://localhost:8000/docs')
        
    except ImportError:
        print("❌ Modulul 'requests' nu este instalat")
        print("📦 Instalez requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("🔄 Rulează din nou testul")

def show_manual_commands():
    """Afișează comenzile pentru pornire manuală"""
    print("\n🔧 Comenzi pentru pornire manuală:")
    print("=" * 40)
    
    print("\n📦 1. Instalare dependențe:")
    print("   pip install -r requirements_fastapi.txt")
    print("   sau")
    print("   pip install -r requirements_api.txt")
    
    print("\n🚀 2. Pornire servere:")
    print("   FastAPI (recomandat):")
    print("   python fastapi_server.py")
    print("   -> http://localhost:8000/docs")
    print()
    print("   Flask:")
    print("   python api_server.py") 
    print("   -> http://localhost:5000")
    
    print("\n🧪 3. Test endpoint-uri:")
    print("   curl http://localhost:8000/")
    print("   curl http://localhost:8000/api/stats")
    print("   curl http://localhost:8000/api/search?q=ghidon")
    print("   curl http://localhost:8000/api/handlebars")
    
    print("\n🌐 4. Client test HTML:")
    client_path = Path("test_client.html").absolute()
    print(f"   file://{client_path}")
    
    print("\n💡 Pentru oprire: Ctrl+C în terminal")

def main():
    print("🚴‍♂️ BikeStylish Dynamic API Launcher")
    print("=" * 50)
    
    # Verifică existența datelor
    if not os.path.exists("data"):
        print("❌ Directorul 'data' nu există!")
        print("   Asigură-te că ești în directorul bikestylish-catalog")
        return
    
    print("📊 Date disponibile:")
    data_files = []
    if os.path.exists("data/products_ai_enhanced.json"):
        data_files.append("✅ products_ai_enhanced.json")
    if os.path.exists("data/products_ai_enhanced_split"):
        split_files = len([f for f in os.listdir("data/products_ai_enhanced_split") if f.endswith('.json')])
        data_files.append(f"✅ {split_files} fișiere split")
    
    for file in data_files:
        print(f"   {file}")
    
    print("\nAlege opțiunea:")
    print("1. 🐍 Flask Server (port 5000)")
    print("2. ⚡ FastAPI Server (port 8000) - Recomandat")
    print("3. 🌐 Deschide doar clientul de test")
    print("4. 📦 Instalează doar dependențele")
    print("5. 🧪 Test rapid API (pornește și testează)")
    print("6. 🔧 Pornire manuală (afișează comenzile)")
    print("0. ❌ Ieșire")
    
    choice = input("\nOpțiunea ta (0-6): ").strip()
    
    if choice == "1":
        if install_requirements("requirements_api.txt"):
            start_flask_server()
    
    elif choice == "2":
        if install_requirements("requirements_fastapi.txt"):
            start_fastapi_server()
    
    elif choice == "3":
        open_test_client()
    
    elif choice == "4":
        print("Alege ce dependențe să instalez:")
        print("1. Flask")
        print("2. FastAPI")
        print("3. Ambele")
        
        dep_choice = input("Opțiunea ta (1-3): ").strip()
        
        if dep_choice == "1":
            install_requirements("requirements_api.txt")
        elif dep_choice == "2":
            install_requirements("requirements_fastapi.txt")
        elif dep_choice == "3":
            install_requirements("requirements_api.txt")
            install_requirements("requirements_fastapi.txt")
    
    elif choice == "5":
        test_api_quick()
    
    elif choice == "6":
        show_manual_commands()
    
    elif choice == "0":
        print("👋 La revedere!")
    
    else:
        print("❌ Opțiune invalidă!")

if __name__ == "__main__":
    main()
