# 🚀 BikeStylish API - Ghid Rapid

## ⚡ Pornire Rapidă (cel mai simplu)

### Windows:
```cmd
# Dublu-click pe start_api.bat
# SAU în command prompt:
start_api.bat
```

### Python:
```bash
python quick_start.py
```

## 🔧 Pornire cu Opțiuni

```bash
python start_api.py
```

Apoi alege:
- **2** - FastAPI Server (recomandat)
- **5** - Test rapid (pornește și testează automat)

## 🧪 Testare API

După ce serverul pornește:

```bash
# Testează toate endpoint-urile
python test_endpoints.py

# SAU deschide în browser:
http://localhost:8000/docs
```

## 📡 Endpoint-uri Principale

| Endpoint | Descriere | Exemplu |
|----------|-----------|---------|
| `GET /` | Info API | http://localhost:8000/ |
| `GET /docs` | Documentație Swagger | http://localhost:8000/docs |
| `GET /api/search` | Căutare produse | http://localhost:8000/api/search?q=ghidon |
| `GET /api/handlebars` | Ghidoane și componente | http://localhost:8000/api/handlebars |
| `GET /api/stats` | Statistici | http://localhost:8000/api/stats |

## 🔍 Căutări Utile

### Ghidoane:
```
/api/search?q=ghidon&limit=20
/api/handlebars?limit=50
```

### Brand-uri populare:
```
/api/search?brand=SHIMANO&limit=10
/api/search?brand=M-WAVE&limit=10
/api/search?brand=ZOOM&limit=10
```

### Filtrare preț:
```
/api/search?min_price=100&max_price=300&limit=10
/api/search?q=ghidon&max_price=200
```

### Doar în stoc:
```
/api/search?availability=in_stock&limit=10
```

## 🛠️ Depanare

### ❌ "Import fastapi could not be resolved"
```bash
pip install -r requirements_fastapi.txt
```

### ❌ "Connection refused"
- Verifică că serverul rulează
- Reîncearcă cu `python quick_start.py`

### ❌ "Nu s-a găsit directorul data"
- Asigură-te că ești în `bikestylish-catalog/`
- Verifică că există `data/products_ai_enhanced.json`

### ❌ Server blochează terminalul
- **Normal!** Serverul rulează continuu
- Pentru oprire: **Ctrl+C**
- Pentru background: rulează în alt terminal

## 📱 Integrare în Aplicații

### JavaScript/Web:
```javascript
fetch('http://localhost:8000/api/search?q=ghidon')
  .then(response => response.json())
  .then(data => console.log(data.results));
```

### Python:
```python
import requests

response = requests.get('http://localhost:8000/api/handlebars')
handlebars = response.json()['by_type']['handlebars']
```

### cURL:
```bash
curl "http://localhost:8000/api/search?q=ghidon&limit=5"
```

## 🎯 Exemple Concrete

### Găsește ghidoane MTB sub 150 RON:
```
http://localhost:8000/api/search?q=ghidon MTB&max_price=150
```

### Toate produsele SHIMANO în stoc:
```
http://localhost:8000/api/search?brand=SHIMANO&availability=in_stock
```

### Componente de ghidoane (pipa, ghidolina):
```
http://localhost:8000/api/handlebars?limit=100
```

---

**💡 Pentru suport tehnic, consultă `API_README.md` pentru detalii complete!**
