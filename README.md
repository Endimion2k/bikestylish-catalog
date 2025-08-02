# 🚴 BikeStylish API - Catalog Complet

![API Status](https://img.shields.io/badge/API-LIVE-brightgreen)
![Products](https://img.shields.io/badge/Produse-5437-blue)
![Categories](https://img.shields.io/badge/Categorii-101-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Despre

API REST gratuit pentru accesul la catalogul complet BikeStylish.ro cu **5437 produse** și **101 categorii** organizate în fișiere JSON optimizate pentru performanță.

## 🚀 API Live

**Base URL:** `https://endimion2k.github.io/bikestylish-catalog/`

### 📦 Endpoints Produse (27 părți)
```
https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_XX.json
```
*Înlocuiește XX cu 01, 02, 03... 27*

### 📂 Endpoints Categorii (26 părți)  
```
https://endimion2k.github.io/bikestylish-catalog/data/categories_ai_enhanced_split/categories_ai_enhanced_part_XX.json
```
*Înlocuiește XX cu 01, 02, 03... 26*

## 💻 Exemple de Cod

### JavaScript
```javascript
// Încarcă primul set de produse
fetch('https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_01.json')
  .then(response => response.json())
  .then(data => {
    console.log('Produse încărcate:', data.products.length);
    data.products.forEach(product => {
      console.log(`${product.name} - ${product.price} RON`);
    });
  });
```

### Python
```python
import requests

def load_all_products():
    all_products = []
    base_url = "https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/"
    
    for i in range(1, 28):
        part_num = str(i).zfill(2)
        url = f"{base_url}products_ai_enhanced_part_{part_num}.json"
        
        response = requests.get(url)
        data = response.json()
        all_products.extend(data['products'])
        
        print(f"Partea {i}: {len(data['products'])} produse")
    
    return all_products

products = load_all_products()
print(f"Total: {len(products)} produse încărcate")
```

### cURL
```bash
# Test endpoint produse
curl -X GET "https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_01.json"

# Test endpoint categorii  
curl -X GET "https://endimion2k.github.io/bikestylish-catalog/data/categories_ai_enhanced_split/categories_ai_enhanced_part_01.json"
```

## 📊 Structura Datelor

### Format Produse
```json
{
  "last_updated": "2025-07-28T22:39:01.000000",
  "total_products": 203,
  "version": "2.0.0",
  "source": "bikestylish.ro",
  "part_info": {
    "part_number": 1,
    "total_parts": 27,
    "products_range": "1-203"
  },
  "products": [
    {
      "id": "product_id",
      "name": "Nume Produs",
      "price": 1999.99,
      "category": "Categorie",
      "stock": 5,
      "description": "Descriere detaliată...",
      "images": ["url1", "url2"],
      "brand": "Brand",
      "specifications": {...}
    }
  ]
}
```

### Format Categorii
```json
{
  "last_updated": "2025-07-28T22:39:01.000000",
  "total_categories": 4,
  "version": "2.0.0",
  "source": "bikestylish.ro",
  "part_info": {
    "part_number": 1,
    "total_parts": 26,
    "categories_range": "1-4"
  },
  "categories": [
    {
      "id": "category_id",
      "name": "Nume Categorie",
      "description": "Descriere...",
      "products_count": 150,
      "subcategories": [...],
      "parent_id": null
    }
  ]
}
```

## 🔧 Funcționalități

- ✅ **API REST complet** - GET requests pentru toate datele
- ✅ **CORS activat** - funcționează din browser și aplicații
- ✅ **HTTPS SSL** - securitate maximă
- ✅ **Cache optimizat** - performanță rapidă
- ✅ **Fără limite** de rate limiting
- ✅ **Documentație completă** - cu exemple în multiple limbi
- ✅ **Format JSON** - ușor de parserat și integrat

## 📈 Statistici

| Metric | Valoare |
|--------|---------|
| **Total Produse** | 5,437 |
| **Total Categorii** | 101 |
| **Fișiere JSON** | 53 |
| **Dimensiune Totală** | 34.57 MB |
| **Părți Produse** | 27 |
| **Părți Categorii** | 26 |
| **Ultima Actualizare** | 28 Iulie 2025 |

## 🛠️ Utilizare Avansată

### Încărcarea Tuturor Produselor
```javascript
async function loadAllProducts() {
  const allProducts = [];
  const baseUrl = 'https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/';
  
  for (let i = 1; i <= 27; i++) {
    const partNumber = i.toString().padStart(2, '0');
    const response = await fetch(`${baseUrl}products_ai_enhanced_part_${partNumber}.json`);
    const data = await response.json();
    allProducts.push(...data.products);
  }
  
  return allProducts;
}
```

### Filtrare și Căutare
```javascript
async function searchProducts(query, category = null) {
  const products = await loadAllProducts();
  
  return products.filter(product => {
    const matchesQuery = product.name.toLowerCase().includes(query.toLowerCase()) ||
                        product.description.toLowerCase().includes(query.toLowerCase());
    const matchesCategory = !category || product.category === category;
    
    return matchesQuery && matchesCategory;
  });
}

// Exemplu: găsește toate bicicletele MTB
const mtbBikes = await searchProducts('MTB', 'Biciclete');
```

## 📝 Rate Limits și Politici

- **Rate Limits:** Fără limite pentru GitHub Pages
- **Cache:** 1 oră pentru fișierele JSON
- **CORS:** Permis pentru toate domeniile (`*`)
- **SSL:** HTTPS obligatoriu
- **Disponibilitate:** 99.9% uptime garantat de GitHub

## 🌐 Alternative CDN

Pentru performanță și redundanță, poți folosi și:

### jsDelivr CDN
```
https://cdn.jsdelivr.net/gh/Endimion2k/bikestylish-catalog@main/data/products_ai_enhanced_split/products_ai_enhanced_part_01.json
```

### GitHub Raw (backup)
```
https://raw.githubusercontent.com/Endimion2k/bikestylish-catalog/main/data/products_ai_enhanced_split/products_ai_enhanced_part_01.json
```

## 🔒 Securitate

- ✅ **HTTPS SSL** - toate cererile sunt criptate
- ✅ **Read-only** - nu se pot modifica datele
- ✅ **Fără autentificare** - API public și gratuit
- ✅ **Headers securizate** - protecție împotriva atacurilor

## 📞 Suport și Contact

- **Website:** [bikestylish.ro](https://www.bikestylish.ro)
- **Email:** office@bikestylish.ro
- **GitHub Issues:** [Raportează o problemă](https://github.com/Endimion2k/bikestylish-catalog/issues)
- **API Documentation:** [Documentație completă](https://endimion2k.github.io/bikestylish-catalog/)

## 📄 Licență

Acest API este oferit gratuit pentru:
- ✅ **Dezvoltare și testare**
- ✅ **Proiecte educaționale**  
- ✅ **Aplicații non-comerciale**
- ✅ **Cercetare și analiză**

Pentru utilizare comercială, contactați office@bikestylish.ro

## 🚀 Cum să Începi

1. **Testează API-ul:**
   ```bash
   curl https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_01.json
   ```

2. **Vizualizează documentația:**
   ```
   https://endimion2k.github.io/bikestylish-catalog/
   ```

3. **Integrează în aplicația ta** folosind exemplele de cod de mai sus

---

**🎯 API-ul este LIVE și funcțional! Începe să dezvolți acum!**