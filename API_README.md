# 🚴‍♂️ BikeStylish Dynamic API

API dinamic creat din datele statice BikeStylish cu **5,437+ produse** de biciclete și componente.

## 🚀 Quick Start

```bash
# 1. Navighează în director
cd bikestylish-catalog

# 2. Pornește API-ul
python start_api.py

# 3. Alege opțiunea 2 (FastAPI - recomandat)
```

## 📡 Endpoint-uri Disponibile

### Flask Server (port 5000)
```
http://localhost:5000/
http://localhost:5000/api/products
http://localhost:5000/api/products/search?q=ghidon
http://localhost:5000/api/handlebars
http://localhost:5000/api/categories
http://localhost:5000/api/brands
http://localhost:5000/api/stats
```

### FastAPI Server (port 8000) - Recomandat
```
http://localhost:8000/
http://localhost:8000/docs  (Documentație Swagger)
http://localhost:8000/api/products
http://localhost:8000/api/search?q=ghidon
http://localhost:8000/api/handlebars
```

## 🔍 Exemple de Căutare

### Căutare Ghidoane
```bash
curl "http://localhost:8000/api/search?q=ghidon&limit=10"
```

### Filtrare pe Brand și Preț
```bash
curl "http://localhost:8000/api/search?brand=SHIMANO&min_price=100&max_price=500"
```

### Doar Produse în Stoc
```bash
curl "http://localhost:8000/api/search?availability=in_stock"
```

### Endpoint Special Ghidoane
```bash
curl "http://localhost:8000/api/handlebars?limit=50"
```

## 📊 Exemple Răspunsuri

### Căutare Ghidoane
```json
{
  "query": "ghidon",
  "results": [
    {
      "id": "ghidon-mtb-zoom-31-8-720mm",
      "name": "Ghidon MTB ZOOM 31.8- 720 mm Rise 20 mm Negru",
      "brand": "ZOOM",
      "category": "accesorii",
      "price": 110.0,
      "currency": "RON",
      "availability": "in_stock",
      "stock_quantity": 5,
      "description": "Ghidon MTB din aluminiu...",
      "url": "https://www.bikestylish.ro/..."
    }
  ],
  "count": 157
}
```

### Ghidoane Grupate
```json
{
  "total_handlebars": 157,
  "by_type": {
    "stems": [
      {
        "name": "Pipa M-WAVE 31.8/100 mm Negru",
        "price": 65.0,
        "brand": "M-WAVE"
      }
    ],
    "handlebars": [
      {
        "name": "Ghidon Racing ZOOM 440/31.8 mm",
        "price": 170.0,
        "brand": "ZOOM"
      }
    ],
    "handlebar_tape": [...],
    "accessories": [...]
  }
}
```

## 🛠️ Instalare Manuală

### Pentru Flask
```bash
pip install -r requirements_api.txt
python api_server.py
```

### Pentru FastAPI
```bash
pip install -r requirements_fastapi.txt
python fastapi_server.py
```

## 🌐 Client de Test

Deschide `test_client.html` în browser pentru o interfață grafică de testare.

## 📁 Structura Datelor

```
data/
├── products_ai_enhanced.json     # Toate produsele
├── products_ai_enhanced_split/   # Produse împărțite în părți
├── categories_ai_enhanced.json   # Categorii
└── brands.json                   # Branduri
```

## 🔧 Caracteristici API

- ✅ **5,437+ produse** din BikeStylish.ro
- ✅ **Căutare full-text** în nume și descrieri
- ✅ **Filtrare avansată** pe categorie, brand, preț, disponibilitate
- ✅ **Endpoint special ghidoane** cu grupare pe tipuri
- ✅ **Paginare** pentru liste mari
- ✅ **CORS** activat pentru integrare web
- ✅ **Documentație Swagger** (FastAPI)
- ✅ **Validare** parametri cu Pydantic

## 🎯 Use Cases

### 1. E-commerce Integration
```javascript
// Căutare produse în JavaScript
fetch('http://localhost:8000/api/search?q=ghidon&limit=20')
  .then(response => response.json())
  .then(data => console.log(data.results));
```

### 2. Mobile App Backend
```python
import requests

# API call din Python
response = requests.get('http://localhost:8000/api/handlebars')
handlebars = response.json()['by_type']['handlebars']
```

### 3. Analytics Dashboard
```bash
# Statistici pentru dashboard
curl "http://localhost:8000/api/stats"
```

## 🔍 Găsit în Căutările Noastre

Prin căutarea **"ghidon"** am identificat:

- **157+ produse** legate de ghidoane
- **Stems (pipa)**: 89 produse
- **Handlebars (ghidon)**: 45 produse  
- **Handlebar tape (ghidolina)**: 12 produse
- **Accessories**: 11 produse

### Branduri Top Ghidoane
- ZOOM, M-WAVE, SXT, DEDA, SHIMANO
- Prețuri: 55-650 RON
- Categorii: MTB, Racing, Touring, Trekking

## 📈 Performance

- **Timp răspuns**: <100ms pentru căutări simple
- **Memorie**: ~50MB pentru toate datele
- **Concurrent requests**: Suportat via FastAPI async

## 🔧 Customizare

Pentru a adăuga noi endpoint-uri, editează:
- `fastapi_server.py` - pentru FastAPI
- `api_server.py` - pentru Flask

Exemple de endpoint-uri noi:
```python
@app.get("/api/products/popular")
async def get_popular_products():
    # Produse cu rating înalt
    popular = [p for p in data_store.products if p.get('rating', 0) > 4.5]
    return {"popular_products": popular[:20]}

@app.get("/api/deals")
async def get_deals():
    # Produse cu discount
    deals = [p for p in data_store.products if p.get('discount_percent', 0) > 20]
    return {"deals": deals}
```

## 📞 Support

Pentru probleme sau întrebări:
1. Verifică că datele există în `data/`
2. Rulează `python start_api.py` și alege opțiunea 4 pentru dependențe
3. Testează endpoint-urile cu `test_client.html`

---

**🎉 Acum ai un API complet funcțional cu toate datele BikeStylish!**
