#!/usr/bin/env python3
"""
Script pentru backup-ul fișierului JSON înainte de procesare.
Creează copii de siguranță cu timestamp-uri.
"""

import json
import shutil
from datetime import datetime
import os

def create_backup(json_file):
    """Creează un backup al fișierului JSON"""
    if not os.path.exists(json_file):
        print(f"❌ Fișierul {json_file} nu există!")
        return False
    
    # Creează directorul de backup dacă nu există
    backup_dir = os.path.dirname(json_file) + "/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generează numele fișierului de backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(json_file)
    name, ext = os.path.splitext(filename)
    backup_filename = f"{name}_backup_{timestamp}{ext}"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copiază fișierul
        shutil.copy2(json_file, backup_path)
        print(f"✅ Backup creat: {backup_path}")
        
        # Verifică integritatea JSON-ului
        with open(backup_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            categories_count = len(data.get('categories', []))
            print(f"📊 Backup verificat: {categories_count} categorii")
        
        return backup_path
        
    except Exception as e:
        print(f"❌ Eroare la crearea backup-ului: {e}")
        return False

def cleanup_old_backups(backup_dir, keep_count=5):
    """Păstrează doar ultimele N backup-uri"""
    try:
        if not os.path.exists(backup_dir):
            return
        
        # Găsește toate backup-urile
        backups = []
        for file in os.listdir(backup_dir):
            if file.startswith("categories_ai_enhanced_backup_") and file.endswith(".json"):
                file_path = os.path.join(backup_dir, file)
                backups.append((file_path, os.path.getctime(file_path)))
        
        # Sortează după data creării (cel mai nou primul)
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Șterge backup-urile vechi
        if len(backups) > keep_count:
            for backup_path, _ in backups[keep_count:]:
                os.remove(backup_path)
                print(f"🗑️  Șters backup vechi: {os.path.basename(backup_path)}")
        
        print(f"📁 Păstrate {min(len(backups), keep_count)} backup-uri")
        
    except Exception as e:
        print(f"❌ Eroare la curățarea backup-urilor: {e}")

def list_backups(json_file):
    """Listează toate backup-urile disponibile"""
    backup_dir = os.path.dirname(json_file) + "/backups"
    
    if not os.path.exists(backup_dir):
        print("📁 Nu există backup-uri")
        return
    
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith("categories_ai_enhanced_backup_") and file.endswith(".json"):
            file_path = os.path.join(backup_dir, file)
            created_time = datetime.fromtimestamp(os.path.getctime(file_path))
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            backups.append((file, created_time, file_size))
    
    if not backups:
        print("📁 Nu există backup-uri")
        return
    
    # Sortează după data creării
    backups.sort(key=lambda x: x[1], reverse=True)
    
    print("📋 BACKUP-URI DISPONIBILE:")
    print("-" * 60)
    for i, (filename, created_time, size_mb) in enumerate(backups, 1):
        print(f"{i:2d}. {filename}")
        print(f"    📅 {created_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    📏 {size_mb:.1f} MB")
        print()

def main():
    json_file = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    
    print("🔄 SISTEM BACKUP CATEGORII BIKESTYLISH")
    print("=" * 50)
    
    # Creează backup
    backup_path = create_backup(json_file)
    
    if backup_path:
        # Curăță backup-urile vechi
        backup_dir = os.path.dirname(backup_path)
        cleanup_old_backups(backup_dir, keep_count=5)
        
        print("\n📋 Backup-uri disponibile:")
        list_backups(json_file)
        
        print("\n✅ Backup creat cu succes!")
        print("🚀 Acum poți rula în siguranță:")
        print("   python auto_update_categories.py")
    else:
        print("\n❌ Backup-ul a eșuat!")

if __name__ == "__main__":
    main()
