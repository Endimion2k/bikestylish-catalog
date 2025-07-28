#!/usr/bin/env python3
"""
Script principal pentru actualizarea automată a categoriilor BikeStylish.
Orchestrează backup-ul, monitorizarea și procesarea automată.
"""

import sys
import os
import subprocess
from datetime import datetime

def run_script(script_name, description):
    """Rulează un script Python și returnează True dacă reușește"""
    try:
        print(f"\n🔄 {description}...")
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            print(result.stdout)
            return True
        else:
            print(f"❌ {description} - EROARE")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Eroare la rularea {script_name}: {e}")
        return False

def check_dependencies():
    """Verifică dacă sunt instalate dependențele necesare"""
    required_packages = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4')
    ]
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Lipsesc dependențele următoare:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n📦 Pentru a instala, rulează:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Funcția principală"""
    print("🚀 ACTUALIZARE AUTOMATĂ CATEGORII BIKESTYLISH")
    print("=" * 55)
    print(f"📅 Început: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verifică dependențele
    print("\n🔍 Verificare dependențe...")
    if not check_dependencies():
        print("\n❌ Instalează dependențele și încearcă din nou.")
        return
    print("✅ Dependențele sunt instalate")
    
    # Schimbă directorul la locația scripturilor
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📂 Director de lucru: {script_dir}")
    
    # 1. Verifică progresul curent
    if not run_script("monitor_progress.py", "Verificare progres curent"):
        print("⚠️  Continuă cu procesarea...")
    
    # Întreabă utilizatorul dacă vrea să continue
    print("\n" + "="*55)
    response = input("🤔 Vrei să continui cu procesarea automată? (y/n): ").strip().lower()
    if response not in ['y', 'yes', 'da']:
        print("🛑 Procesare anulată de utilizator")
        return
    
    # 2. Creează backup
    if not run_script("backup_json.py", "Creare backup"):
        print("⚠️  Backup eșuat, dar continuă procesarea...")
    
    # 3. Rulează procesarea automată
    print("\n" + "="*55)
    print("🔄 ÎNCEPE PROCESAREA AUTOMATĂ")
    print("   • Aceasta poate dura 30-60 minute")
    print("   • Progresul va fi salvat la fiecare 3 categorii")
    print("   • Poți opri cu Ctrl+C și relua mai târziu")
    print("="*55)
    
    if not run_script("auto_update_categories.py", "Procesare automată categorii"):
        print("❌ Procesarea a întâmpinat erori")
        return
    
    # 4. Afișează raportul final
    print("\n" + "="*55)
    run_script("monitor_progress.py", "Raport final")
    
    print(f"\n🎉 PROCESARE COMPLETĂ!")
    print(f"📅 Sfârșit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*55)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Procesare oprită de utilizator")
        print("🔄 Pentru a relua, rulează din nou scriptul")
    except Exception as e:
        print(f"\n❌ Eroare neașteptată: {e}")
        print("🔄 Verifică log-urile și încearcă din nou")
