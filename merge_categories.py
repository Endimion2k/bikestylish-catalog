import json
import os
import glob

def merge_split_categories_files(split_directory, output_file):
    """
    Reunește fișierele JSON cu categorii împărțite înapoi într-un singur fișier.
    
    Args:
        split_directory (str): Directorul care conține fișierele împărțite
        output_file (str): Calea pentru fișierul de ieșire
    """
    print(f"Căutare fișiere în: {split_directory}")
    
    # Găsește toate fișierele part_XX.json
    pattern = os.path.join(split_directory, "*_part_*.json")
    part_files = sorted(glob.glob(pattern))
    
    if not part_files:
        print("Nu s-au găsit fișiere de tip part_XX.json")
        return
    
    print(f"Găsite {len(part_files)} fișiere de unit")
    
    # Încarcă primul fișier pentru a obține structura de bază
    with open(part_files[0], 'r', encoding='utf-8') as f:
        base_data = json.load(f)
    
    # Inițializează lista de categorii unită
    all_categories = []
    
    # Procesează fiecare fișier
    for i, part_file in enumerate(part_files):
        print(f"Procesare fișier {i+1}/{len(part_files)}: {os.path.basename(part_file)}")
        
        with open(part_file, 'r', encoding='utf-8') as f:
            part_data = json.load(f)
        
        # Adaugă categoriile din acest fișier
        if 'categories' in part_data:
            all_categories.extend(part_data['categories'])
            print(f"  - Adăugate {len(part_data['categories'])} categorii")
        elif 'hierarchy' in part_data and 'main_categories' in part_data['hierarchy']:
            all_categories.extend(part_data['hierarchy']['main_categories'])
            print(f"  - Adăugate {len(part_data['hierarchy']['main_categories'])} categorii din hierarchy")
    
    # Actualizează structura finală
    base_data['categories'] = all_categories
    base_data['total_categories'] = len(all_categories)
    
    # Elimină informațiile de împărțire
    if 'part_info' in base_data:
        del base_data['part_info']
    
    # Salvează fișierul unit
    print(f"Salvare fișier unit: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)
    
    # Verifică dimensiunea finală
    final_size_bytes = os.path.getsize(output_file)
    final_size_mb = final_size_bytes / (1024 * 1024)
    
    print(f"Fișierul unit creat cu succes!")
    print(f"Total categorii: {len(all_categories)}")
    print(f"Dimensiunea finală: {final_size_mb:.2f} MB")

if __name__ == "__main__":
    split_dir = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced_split"
    output_file = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced_merged.json"
    
    if not os.path.exists(split_dir):
        print(f"Eroare: Directorul {split_dir} nu există!")
    else:
        merge_split_categories_files(split_dir, output_file)
