import json
import os
import math

def split_json_file(input_file, max_size_mb=1):
    """
    Împarte un fișier JSON mare în mai multe fișiere mai mici.
    
    Args:
        input_file (str): Calea către fișierul JSON de intrare
        max_size_mb (float): Dimensiunea maximă pentru fiecare fișier în MB
    """
    print(f"Încărcare fișier: {input_file}")
    
    # Încarcă datele JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
    
    # Extrage lista de produse din structura JSON
    if not isinstance(full_data, dict) or 'products' not in full_data:
        print("Eroare: Fișierul JSON trebuie să conțină un obiect cu cheia 'products'")
        return
    
    products_data = full_data['products']
    if not isinstance(products_data, list):
        print("Eroare: Secțiunea 'products' trebuie să fie o listă")
        return
    
    total_items = len(products_data)
    print(f"Total produse: {total_items}")
    
    # Calculează dimensiunea aproximativă per element
    file_size_bytes = os.path.getsize(input_file)
    file_size_mb = file_size_bytes / (1024 * 1024)
    avg_item_size_bytes = file_size_bytes / total_items
    
    print(f"Dimensiunea fișierului original: {file_size_mb:.2f} MB")
    print(f"Dimensiunea medie per produs: {avg_item_size_bytes:.2f} bytes")
    
    # Calculează câte elemente pe fișier
    max_size_bytes = max_size_mb * 1024 * 1024
    items_per_file = int(max_size_bytes / avg_item_size_bytes)
    
    # Asigură-te că nu depășești limita
    if items_per_file <= 0:
        items_per_file = 1
    
    print(f"Produse per fișier: {items_per_file}")
    
    # Calculează numărul de fișiere necesare
    num_files = math.ceil(total_items / items_per_file)
    print(f"Numărul estimat de fișiere: {num_files}")
    
    # Creează directorul pentru fișierele împărțite
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(os.path.dirname(input_file), f"{base_name}_split")
    os.makedirs(output_dir, exist_ok=True)
    
    # Împarte datele și salvează fișierele
    for i in range(num_files):
        start_idx = i * items_per_file
        end_idx = min((i + 1) * items_per_file, total_items)
        
        chunk_data = products_data[start_idx:end_idx]
        
        # Creează structura JSON pentru chunk-ul curent
        chunk_json = {
            "last_updated": full_data.get("last_updated", ""),
            "total_products": len(chunk_data),
            "version": full_data.get("version", ""),
            "source": full_data.get("source", ""),
            "part_info": {
                "part_number": i + 1,
                "total_parts": num_files,
                "products_range": f"{start_idx + 1}-{end_idx}"
            },
            "categories": full_data.get("categories", []),
            "brands": full_data.get("brands", []),
            "products": chunk_data
        }
        
        # Nume fișier cu zero padding pentru sortare corectă
        output_file = os.path.join(output_dir, f"{base_name}_part_{i+1:02d}.json")
        
        # Salvează chunk-ul
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_json, f, ensure_ascii=False, indent=2)
        
        # Verifică dimensiunea fișierului creat
        chunk_size_bytes = os.path.getsize(output_file)
        chunk_size_mb = chunk_size_bytes / (1024 * 1024)
        
        print(f"Fișier {i+1}/{num_files}: {os.path.basename(output_file)} - {len(chunk_data)} produse - {chunk_size_mb:.2f} MB")
    
    print(f"\nÎmpărțirea completă! Fișierele au fost salvate în: {output_dir}")
    
    # Crează un fișier de informații
    info_file = os.path.join(output_dir, "split_info.txt")
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(f"Informații despre împărțirea fișierului {os.path.basename(input_file)}\n")
        f.write(f"Data împărțirii: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Fișier original: {file_size_mb:.2f} MB, {total_items} produse\n")
        f.write(f"Numărul de fișiere create: {num_files}\n")
        f.write(f"Produse per fișier: {items_per_file}\n")
        f.write(f"Dimensiunea țintă per fișier: {max_size_mb} MB\n\n")
        f.write("Lista fișierelor create:\n")
        
        for i in range(num_files):
            start_idx = i * items_per_file
            end_idx = min((i + 1) * items_per_file, total_items)
            f.write(f"- {base_name}_part_{i+1:02d}.json: produse {start_idx+1}-{end_idx}\n")

if __name__ == "__main__":
    input_file = r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\products_ai_enhanced.json"
    
    if not os.path.exists(input_file):
        print(f"Eroare: Fișierul {input_file} nu există!")
    else:
        split_json_file(input_file, max_size_mb=1.0)
