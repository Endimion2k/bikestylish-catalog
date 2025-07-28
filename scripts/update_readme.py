#!/usr/bin/env python3
"""
Update README with complete category information
"""

import json
from datetime import datetime

def generate_updated_readme():
    """Generate updated README with complete category structure."""
    
    print("📝 Updating README with category information...")
    
    # Load category data
    with open('../data/categories_detailed.json', 'r', encoding='utf-8') as f:
        categories_data = json.load(f)
    
    # Load main catalog
    with open('../data/products_ai_enhanced.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    categories = categories_data['categories']
    hierarchy = categories_data['hierarchy']
    mappings = categories_data['mappings']
    
    # Get statistics safely
    total_products = len(catalog.get('products', []))
    metadata = catalog.get('metadata', {})
    
    readme_content = f"""# BikeStylish Catalog API

🚴‍♂️ **Complete AI-Enhanced Product Catalog for BikeStylish.ro**

## 📊 Overview

- **Total Products**: {total_products:,} AI-enhanced products
- **Categories**: {len(categories)} structured categories  
- **URL Coverage**: {metadata.get('url_coverage', 'N/A')}% ({metadata.get('unique_urls', 'N/A')} unique URLs)
- **Brands**: {metadata.get('total_brands', 'N/A')} brands
- **File Size**: {metadata.get('file_size', 'N/A')}MB
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🗂️ Category Structure

### Main Category Types ({len(mappings['type_groups'])} types)

"""
    
    # Add category type breakdown
    for cat_type, cat_list in mappings['type_groups'].items():
        readme_content += f"#### {cat_type.upper()} ({len(cat_list)} categories)\n"
        
        # Get sample categories for this type
        sample_cats = [cat for cat in categories if cat['type'] == cat_type][:5]
        for cat in sample_cats:
            readme_content += f"- **{cat['name']}** - {cat['id']}\n"
        
        if len(sample_cats) < len(cat_list):
            readme_content += f"- *...and {len(cat_list) - len(sample_cats)} more*\n"
        
        readme_content += "\n"
    
    readme_content += f"""
### Hierarchical Structure

**Main Categories**: {len(hierarchy['main_categories'])}
**Subcategories**: {sum(len(subs) for subs in hierarchy['subcategories'].values())}

### Complete Category List

<details>
<summary>View All {len(categories)} Categories</summary>

"""
    
    # Add all categories grouped by type
    for cat_type, cat_list in mappings['type_groups'].items():
        readme_content += f"#### {cat_type.upper()}\n"
        
        type_categories = [cat for cat in categories if cat['type'] == cat_type]
        for cat in sorted(type_categories, key=lambda x: x['name']):
            readme_content += f"- [{cat['name']}]({cat['url']}) (`{cat['id']}`)\n"
        
        readme_content += "\n"
    
    readme_content += """
</details>

## 🔧 API Features

### Product Data Structure
```json
{
  "id": "unique_product_id",
  "nume_produs": "Product Name",
  "pret_sugerat": 22.0,
  "pret_produs": 18.0,
  "descriere": "Detailed description",
  "url": "https://www.bikestylish.ro/product-url",
  "brand": "Brand Name",
  "categorie": "Category",
  "ai_metadata": {
    "enhanced_description": "AI-enhanced description",
    "search_keywords": ["keyword1", "keyword2"],
    "technical_specs": {...},
    "multilingual_terms": {...}
  },
  "ai_context": {...},
  "search_optimization": {...},
  "faq_schema": {...},
  "technical_specifications": {...}
}
```

### AI Enhancement Features
- ✅ **Enhanced Descriptions**: AI-generated detailed product descriptions
- ✅ **Multilingual Search Terms**: Romanian, English, and German keywords
- ✅ **Technical Specifications**: Structured technical data
- ✅ **FAQ Schema**: Automated frequently asked questions
- ✅ **Search Optimization**: Enhanced search and filtering capabilities
- ✅ **Schema Markup**: Structured data for better SEO
- ✅ **Category Mapping**: Complete hierarchical category structure

## 📁 File Structure

```
bikestylish-catalog/
├── data/
│   ├── products_ai_enhanced.json      # Main AI-enhanced catalog (897MB)
│   ├── categories_detailed.json       # Detailed category structure
│   ├── products.json                  # Original catalog
│   └── products_enhanced.json         # Basic enhanced version
├── scripts/
│   ├── enhance_catalog_for_ai.py      # AI enhancement engine
│   ├── parse_categories.py            # Category parser
│   └── validate_for_github.py         # Repository validator
├── docs/
│   ├── API_DOCUMENTATION.md          # Complete API documentation
│   ├── AI_OPTIMIZATION_GUIDE.md      # AI optimization guide
│   └── GITHUB_UPLOAD_GUIDE.md        # Upload instructions
├── categorii.txt                     # Original sitemap categories
└── README.md                         # This file
```

## 🚀 Usage Examples

### Load Complete Catalog
```python
import json

# Load full AI-enhanced catalog
with open('data/products_ai_enhanced.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

products = catalog['products']
categories = catalog['categories_detailed']
```

### Search by Category
```python
# Get all products in specific category
def get_products_by_category(catalog, category_type):
    products = []
    for product in catalog['products']:
        if product.get('categorie_type') == category_type:
            products.append(product)
    return products

# Example: Get all bicycle accessories
accessories = get_products_by_category(catalog, 'accesorii')
```

### Use AI Features
```python
# Access AI-enhanced features
for product in catalog['products']:
    ai_description = product['ai_metadata']['enhanced_description']
    search_keywords = product['ai_metadata']['search_keywords']
    technical_specs = product['technical_specifications']
    
    # Use multilingual search
    multilingual = product['ai_metadata']['multilingual_terms']
    english_terms = multilingual.get('english', [])
    german_terms = multilingual.get('german', [])
```

## 🔗 API Endpoints

When deployed, the catalog provides these endpoints:

- `GET /products` - All products with filtering
- `GET /products/{id}` - Specific product details
- `GET /categories` - Category hierarchy
- `GET /categories/{type}` - Products by category
- `GET /search?q={query}` - AI-enhanced search
- `GET /brands` - Available brands

## 📈 Statistics

- **Price Range**: {metadata.get('price_range', {}).get('min', 'N/A')} - {metadata.get('price_range', {}).get('max', 'N/A')} RON
- **Average Price**: {metadata.get('price_range', {}).get('average', 'N/A')} RON
- **AI Enhancement Coverage**: 100% (all products enhanced)
- **URL Match Rate**: {metadata.get('url_coverage', 'N/A')}%
- **Category Coverage**: 100% (all {len(categories)} categories mapped)

## 🛠️ Development

### Requirements
- Python 3.8+
- JSON processing libraries
- Pandas for data manipulation
- OpenAI API (for AI enhancements)

### Scripts
- `enhance_catalog_for_ai.py` - Add AI features to products
- `parse_categories.py` - Parse and structure categories
- `validate_for_github.py` - Validate repository for upload

## 📋 Data Sources

- **Product Data**: sxt26.xls (5,437 products)
- **URL Mappings**: link.txt (2,363 URLs)  
- **Categories**: categorii.txt sitemap ({len(categories)} categories)
- **AI Enhancements**: Generated using advanced AI models

## 🤖 AI Agent Integration

This catalog is optimized for AI agents with:

- **Structured Schema**: JSON-LD compatible product schemas
- **Semantic Search**: Enhanced with multilingual keywords
- **Technical Specs**: Machine-readable specifications
- **FAQ Data**: Pre-generated Q&A for common queries
- **Category Mapping**: Hierarchical category relationships

Perfect for integration with:
- E-commerce AI assistants
- Product recommendation engines
- Inventory management systems
- Customer service chatbots

## 📄 License

MIT License - Free for commercial and personal use.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Repository**: [BikeStylish Catalog](https://github.com/username/bikestylish-catalog)
"""
    
    # Save updated README
    with open('../README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README updated with complete category information!")
    print(f"📊 Added {len(categories)} categories in {len(mappings['type_groups'])} types")
    print(f"📝 Generated {len(readme_content.split('\\n'))} lines of documentation")

if __name__ == "__main__":
    generate_updated_readme()
