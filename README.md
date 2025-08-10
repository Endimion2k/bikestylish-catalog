# 🚴‍♂️ BikeStylish Catalog API

> **Primul API gratuit pentru produse de ciclism din România, optimizat pentru AI și dezvoltatori**

[![API Status](https://img.shields.io/badge/API-Online-green)](https://endimion2k.github.io/bikestylish-catalog/)
[![Version](https://img.shields.io/badge/Version-2.0.0-blue)](https://endimion2k.github.io/bikestylish-catalog/)
[![Products](https://img.shields.io/badge/Products-5620-orange)](https://endimion2k.github.io/bikestylish-catalog/)
[![License](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

## ℹ️ Ce este BikeStylish API?

BikeStylish API este prima platformă deschisă din România care oferă acces gratuit la un catalog complet de produse de ciclism:

- **5,620 produse** cu specificații complete
- **116 categorii** organizate inteligent  
- **Zero autentificare** necesară
- **CORS enabled** pentru toate domeniile
- **AI-optimized** cu metadata bogată pentru machine learning

**👉 [Documentație detaliată și completă aici](README_api.md)**

## 🚀 API Live

**Base URL:** `https://endimion2k.github.io/bikestylish-catalog/`

### 📦 Endpoints Produse (23 părți)
```
https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_XX.json
```
*Înlocuiește XX cu 01, 02, 03... 23*

### 📂 Endpoints Categorii (2 părți)  
```
https://endimion2k.github.io/bikestylish-catalog/data/categories_ai_enhanced_split/categories_ai_enhanced_part_XX.json
```
*Înlocuiește XX cu 01, 02*

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
    
    for i in range(1, 24):  # 01-23
        part_num = str(i).zfill(2)
        url = f"{base_url}products_ai_enhanced_part_{part_num}.json"
        
        response = requests.get(url)
        response.raise_for_status()
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
  "last_updated": "2025-08-10T17:38:17.795483",
  "total_products": 250,
  "version": "2.0.0",
  "source": "bikestylish.ro",
  "part_info": {
    "part_number": 1,
    "total_parts": 23,
    "products_range": "1-250"
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
      "specifications": {"...": "..."
    }
  ]
}
```

### Format Categorii
```json
{
  "last_updated": "2025-08-10T17:35:18.850281",
  "total_categories": 100,
  "version": "2.0.0",
  "source": "bikestylish.ro",
  "part_info": {
    "part_number": 1,
    "total_parts": 2,
    "categories_range": "1-100"
  },
  "categories": [
    {
      "id": "category_id",
      "name": "Nume Categorie",
      "description": "Descriere...",
      "products_count": 150,
      "subcategories": ["..."],
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
| **Total Produse** | 5,620 |
| **Total Categorii** | 116 |
| **Fișiere JSON** | 53 |
| **Dimensiune Totală** | 34.57 MB |
| **Părți Produse** | 23 |
| **Părți Categorii** | 2 |
| **Ultima Actualizare** | 10 August 2025 |

## 🛠️ Utilizare Avansată

### Încărcarea Tuturor Produselor
```javascript
async function loadAllProducts() {
  const allProducts = [];
  const baseUrl = 'https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/';
  
  for (let i = 1; i <= 23; i++) {
    const partNumber = i.toString().padStart(2, '0');
    const response = await fetch(`${baseUrl}products_ai_enhanced_part_${partNumber}.json`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
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
    const name = (product.name || '').toLowerCase();
    const desc = (product.description || '').toLowerCase();
    const matchesQuery = name.includes(query.toLowerCase()) || desc.includes(query.toLowerCase());
    const matchesCategory = !category || (product.category || '').toLowerCase() === category.toLowerCase();
    
    return matchesQuery && matchesCategory;
  });
}

// Exemplu: găsește toate produsele din categoria "accesorii"
const accessories = await searchProducts('accesorii', 'accesorii');
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