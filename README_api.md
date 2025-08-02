# 🚴‍♂️ BikeStylish API v2.0 - Official Documentation

> **Primul API gratuit pentru produse de ciclism din România, optimizat pentru AI și dezvoltatori**

[![API Status](https://img.shields.io/badge/API-Online-green)](https://endimion2k.github.io/bikestylish-catalog/)
[![Version](https://img.shields.io/badge/Version-2.0.0-blue)](https://endimion2k.github.io/bikestylish-catalog/)
[![License](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)
[![CORS](https://img.shields.io/badge/CORS-Enabled-success)](https://endimion2k.github.io/bikestylish-catalog/)

## 🎯 Overview

BikeStylish API oferă acces gratuit la cel mai complet catalog de produse de ciclism din România:

- **5,437 produse** cu specificații complete
- **101 categorii** organizate inteligent  
- **Zero autentificare** necesară
- **CORS enabled** pentru toate domeniile
- **AI-optimized** cu metadata bogată

## 🚀 Quick Start

```javascript
// Încarcă primul set de produse
fetch('https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_01.json')
  .then(response => response.json())
  .then(data => {
    console.log(`Încărcate ${data.products.length} produse`);
  });
```

## 📚 Documentație Detaliată

### 🔗 Endpoints

| Tip | URL Pattern | Părți |
|-----|-------------|-------|
| **Produse** | `/data/products_ai_enhanced_split/products_ai_enhanced_part_{XX}.json` | 01-27 |
| **Categorii** | `/data/categories_ai_enhanced_split/categories_ai_enhanced_part_{XX}.json` | 01-26 |

### 📊 Response Schema

```json
{
  "last_updated": "2025-07-28T22:25:48.418022",
  "total_products": 5437,
  "version": "2.0",
  "source": "https://www.bikestylish.ro",
  "part_info": {
    "current_part": 1,
    "total_parts": 27,
    "products_in_part": 201
  },
  "products": [
    {
      "id": "product-unique-id",
      "name": "Product Name",
      "brand": "Brand Name", 
      "category": "category-name",
      "price": 99.99,
      "currency": "RON",
      "availability": "in_stock",
      "stock_quantity": 10,
      "description": "Product description",
      "warranty": "12 luni",
      "search_optimization": {
        "primary_keywords": ["keyword1", "keyword2"],
        "semantic_keywords": ["concept1", "concept2"],
        "multilingual_terms": {
          "ro": ["termen1", "termen2"],
          "en": ["term1", "term2"],
          "de": ["begriff1", "begriff2"],
          "hu": ["kifejezés1", "kifejezés2"]
        }
      }
    }
  ]
}
```

### 🏷️ Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique product identifier |
| `name` | string | Product display name |
| `brand` | string | Manufacturer brand |
| `category` | string | Product category |
| `price` | number | Current price in RON |
| `availability` | string | Stock status: `in_stock`, `out_of_stock`, `limited` |
| `stock_quantity` | number | Available units |
| `search_optimization` | object | AI-optimized search data |

## 💻 Exemple de Cod

### Python

```python
import requests

def get_products(part_number):
    url = f"https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_{part_number:02d}.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Căutare după categorie
def search_by_category(category, max_parts=5):
    results = []
    for part in range(1, max_parts + 1):
        data = get_products(part)
        matches = [p for p in data['products'] if p['category'] == category]
        results.extend(matches)
    return results

accessories = search_by_category('accesorii')
print(f"Găsite {len(accessories)} accesorii")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function getProducts(partNumber) {
  const url = `https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_${partNumber.toString().padStart(2, '0')}.json`;
  const response = await axios.get(url);
  return response.data;
}

async function searchByBrand(brand, maxParts = 5) {
  const results = [];
  
  for (let part = 1; part <= maxParts; part++) {
    try {
      const data = await getProducts(part);
      const matches = data.products.filter(p => 
        p.brand.toLowerCase() === brand.toLowerCase()
      );
      results.push(...matches);
    } catch (error) {
      console.error(`Error loading part ${part}:`, error.message);
    }
  }
  
  return results;
}

// Usage
searchByBrand('M-WAVE').then(products => {
  console.log(`Found ${products.length} M-WAVE products`);
});
```

### PHP

```php
<?php
function getBikeStylishProducts($partNumber) {
    $url = "https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_" . 
           sprintf("%02d", $partNumber) . ".json";
    
    $data = file_get_contents($url);
    if ($data === FALSE) {
        throw new Exception("Failed to fetch data");
    }
    
    return json_decode($data, true);
}

// Search by price range
function searchByPriceRange($minPrice, $maxPrice, $maxParts = 5) {
    $results = [];
    
    for ($part = 1; $part <= $maxParts; $part++) {
        try {
            $data = getBikeStylishProducts($part);
            $matches = array_filter($data['products'], function($p) use ($minPrice, $maxPrice) {
                return $p['price'] >= $minPrice && $p['price'] <= $maxPrice;
            });
            $results = array_merge($results, $matches);
        } catch (Exception $e) {
            error_log("Error loading part $part: " . $e->getMessage());
        }
    }
    
    return $results;
}

$affordableProducts = searchByPriceRange(0, 50);
echo "Found " . count($affordableProducts) . " products under 50 RON\n";
?>
```

## ⚠️ Error Handling

| Status Code | Description | Action |
|-------------|-------------|---------|
| 200 | Success | Process data normally |
| 404 | Invalid part number | Check part range (01-27 for products) |
| 429 | Rate limited | Implement exponential backoff |
| 500 | Server error | Retry after delay |

## 🛠️ Best Practices

### Performance
- **Cache responses** locally for 1 hour
- **Load parts on-demand** rather than all at once
- **Implement retry logic** for network errors
- **Use compression** (gzip) when available

### Error Handling
```javascript
async function safeFetch(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

## 🤖 AI Integration

### Pentru ChatGPT/Claude/Gemini

```
You are helping users find bicycle products. Use the BikeStylish API:

Base URL: https://endimion2k.github.io/bikestylish-catalog/data/
Endpoints: products_ai_enhanced_split/products_ai_enhanced_part_{01-27}.json

Each product has: name, brand, category, price, availability, and multilingual keywords.
Always check stock_quantity > 0 for availability.
```

### Pentru Machine Learning

API-ul include metadata optimizată pentru ML:
- **Semantic keywords** pentru embedding-uri
- **Multilingual terms** pentru cross-language search  
- **Product relationships** pentru recommendation systems
- **Structured pricing** pentru trend analysis

## 📊 API Specifications

| Metric | Value |
|--------|-------|
| **Total Products** | 5,437 |
| **Total Categories** | 101 |
| **Response Format** | JSON |
| **Max Response Size** | ~1.2MB |
| **CDN** | GitHub Pages Global |
| **Cache TTL** | 1 hour |
| **Uptime SLA** | 99.9% |

## 🔍 Advanced Usage

### Batch Processing
```python
import asyncio
import aiohttp

async def fetch_all_products():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for part in range(1, 28):  # Parts 1-27
            url = f"https://endimion2k.github.io/bikestylish-catalog/data/products_ai_enhanced_split/products_ai_enhanced_part_{part:02d}.json"
            tasks.append(fetch_part(session, url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_products = []
        for result in results:
            if isinstance(result, dict):
                all_products.extend(result.get('products', []))
        
        return all_products

async def fetch_part(session, url):
    async with session.get(url) as response:
        return await response.json()

# Usage
products = asyncio.run(fetch_all_products())
print(f"Total products loaded: {len(products)}")
```

### Data Analysis
```python
import pandas as pd

def analyze_market_data():
    # Load all products
    all_products = []
    for part in range(1, 28):
        data = get_products(part)
        all_products.extend(data['products'])
    
    # Convert to DataFrame
    df = pd.DataFrame(all_products)
    
    # Market analysis
    print("=== MARKET ANALYSIS ===")
    print(f"Total products: {len(df)}")
    print(f"Average price: {df['price'].mean():.2f} RON")
    print(f"Price range: {df['price'].min():.2f} - {df['price'].max():.2f} RON")
    
    # Brand distribution
    print("\n=== TOP BRANDS ===")
    print(df['brand'].value_counts().head(10))
    
    # Category distribution  
    print("\n=== TOP CATEGORIES ===")
    print(df['category'].value_counts().head(10))
    
    # Availability stats
    print("\n=== AVAILABILITY ===")
    print(df['availability'].value_counts())

analyze_market_data()
```

## 📞 Support

- **Homepage:** https://endimion2k.github.io/bikestylish-catalog/
- **Store:** https://www.bikestylish.ro
- **Issues:** Create an issue in this repository
- **Updates:** Follow the RSS feed at `/feed.xml`

## 📄 License

Creative Commons Attribution 4.0 International License. You are free to use this data for any purpose with attribution.

---

**⭐ Dacă folosești API-ul, lasă o stea pe GitHub! Ajută la vizibilitate și dezvoltarea continuă.**

**🚀 BikeStylish - Primul magazin de biciclete din România integrat cu AI**
