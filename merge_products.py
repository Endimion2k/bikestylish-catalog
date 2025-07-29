import json
import os
import glob

def merge_split_files(split_directory, output_file):
    """
    Reunește fișierele JSON împărțite înapoi într-un singur fișier.
    
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
    
    # Inițializează lista de produse unită
    all_products = []
    
    # Procesează fiecare fișier
    for i, part_file in enumerate(part_files):
        print(f"Procesare fișier {i+1}/{len(part_files)}: {os.path.basename(part_file)}")
        
        with open(part_file, 'r', encoding='utf-8') as f:
            part_data = json.load(f)
        
        # Adaugă produsele din acest fișier
        if 'products' in part_data:
            all_products.extend(part_data['products'])
            print(f"  - Adăugate {len(part_data['products'])} produse")
    
    # Actualizează structura finală
    base_data['products'] = all_products
    base_data['total_products'] = len(all_products)
    
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
    print(f"Total produse: {len(all_products)}")
    print(f"Dimensiunea finală: {final_size_mb:.2f} MB")

if __name__ == "__main__":
    split_dir = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\products_ai_enhanced_split"
    output_file = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\products_ai_enhanced_merged.json"
    
    if not os.path.exists(split_dir):
        print(f"Eroare: Directorul {split_dir} nu există!")
    else:
        merge_split_files(split_dir, output_file)
