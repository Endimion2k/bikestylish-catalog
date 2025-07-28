#!/usr/bin/env python3
"""
BikeStylish.ro Real Data Parser

This script parses the sitemap XML and product CSV to create
a complete product catalog with real data from BikeStylish.ro
"""

import csv
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Optional
import html

class BikeStylishDataParser:
    def __init__(self):
        self.sitemap_file = "../../link.txt"
        self.csv_file = "../sxt26.csv"  # Updated path to CSV in parent directory
        self.products = []
        self.categories = {}
        self.brands = {}
        
    def clean_html(self, text: str) -> str:
        """Clean HTML tags and decode entities from text."""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        text = html.unescape(text)
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_category_from_url(self, url: str) -> str:
        """Extract category from product URL."""
        if not url:
            return "accesorii"
            
        url_lower = url.lower()
        
        if "/biciclet" in url_lower:
            return "biciclete"
        elif "/piese" in url_lower or "/anvelope" in url_lower or "/camere" in url_lower:
            return "piese-schimb"
        elif "/accesorii" in url_lower:
            return "accesorii"
        else:
            return "accesorii"
    
    def extract_brand_from_name(self, name: str) -> str:
        """Extract brand name from product name."""
        if not name:
            return "Unknown"
            
        name_upper = name.upper()
        
        # Common bike brands
        brands = [
            "M-WAVE", "KENDA", "VENTURA", "BELELLI", "SXT", "CROSS", 
            "GIANT", "TREK", "SPECIALIZED", "SCOTT", "MERIDA", "CANNONDALE",
            "CONTINENTAL", "SHIMANO", "SRAM", "VELO", "EXUSTAR", "CICLO BONIN",
            "B-RACE", "ACTION"
        ]
        
        for brand in brands:
            if brand in name_upper:
                return brand
                
        # Extract first word as potential brand
        first_word = name.split()[0] if name.split() else "Unknown"
        return first_word.title()
    
    def parse_price(self, price_str: str) -> float:
        """Parse price string to float."""
        if not price_str:
            return 0.0
            
        try:
            # Remove any non-numeric characters except decimal point
            price_clean = re.sub(r'[^\d.]', '', str(price_str))
            return float(price_clean) if price_clean else 0.0
        except:
            return 0.0
    
    def parse_csv_data(self) -> Dict[str, Dict]:
        """Parse the CSV file and return product data indexed by name/code."""
        products_data = {}
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                
                for row in reader:
                    # Create a searchable key from product name
                    name = row.get('nume_produs', '').strip()
                    if not name:
                        continue
                    
                    # Clean name for matching
                    clean_name = re.sub(r'[^\w\s]', '', name.lower())
                    
                    product_data = {
                        'cod_produs': row.get('cod_produs', ''),
                        'cod_ean': row.get('cod_ean', '').strip().strip('"'),
                        'nume_produs': name,
                        'descriere': self.clean_html(row.get('descriere', '')),
                        'nume_categorie': row.get('nume_categorie', ''),
                        'imag_baza': row.get('imag_baza', ''),
                        'cant_stock': int(row.get('cant_stock', 0) or 0),
                        'in_stock': int(row.get('in_stock', 0) or 0),
                        'pret_produs': self.parse_price(row.get('pret_produs', 0)),
                        'pret_sugerat': self.parse_price(row.get('pret_sugerat', 0)),
                        'categorie_path': row.get('categorie_path_subcat', ''),
                        'greutate': row.get('greutate', ''),
                        'producator': row.get('producator', ''),
                        'imag_galerie': row.get('imag_galerie', '')
                    }
                    
                    products_data[clean_name] = product_data
                    # Also index by product code for easier lookup
                    products_data[row.get('cod_produs', '')] = product_data
                    
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            
        return products_data
    
    def parse_sitemap_urls(self) -> List[str]:
        """Parse the sitemap XML and extract product URLs."""
        urls = []
        
        try:
            # Read the file content
            with open(self.sitemap_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all CDATA URLs
            cdata_pattern = r'<!\[CDATA\[\s*(https://www\.bikestylish\.ro/[^]]+)\s*\]\]>'
            matches = re.findall(cdata_pattern, content)
            
            for url in matches:
                url = url.strip()
                if url and ('piese' in url or 'accesorii' in url or 'biciclet' in url):
                    urls.append(url)
                    
        except Exception as e:
            print(f"Error parsing sitemap: {e}")
            
        return urls
    
    def match_url_to_product(self, url: str, products_data: Dict) -> Optional[Dict]:
        """Try to match a URL to a product in the CSV data."""
        # Extract product name from URL
        url_parts = url.split('/')
        if not url_parts:
            return None
            
        # Get the last part (filename) and clean it
        filename = url_parts[-1].replace('.html', '')
        filename_clean = re.sub(r'[^\w\s-]', ' ', filename.lower())
        filename_words = set(w for w in filename_clean.split() if len(w) > 2)  # Filter short words
        
        best_match = None
        best_score = 0
        
        # Try to find best matching product by comparing words
        for key, product in products_data.items():
            if not isinstance(key, str) or key.isdigit():
                continue
                
            # Also try matching against the actual product name
            product_name = product.get('nume_produs', '').lower()
            product_name_clean = re.sub(r'[^\w\s-]', ' ', product_name)
            product_words = set(w for w in product_name_clean.split() if len(w) > 2)
            
            # Calculate word overlap score
            common_words = filename_words.intersection(product_words)
            if len(filename_words) == 0 or len(product_words) == 0:
                continue
                
            score = len(common_words) / max(len(filename_words), len(product_words))
            
            # Bonus for exact brand/model matches
            if any(word in filename_clean for word in ['m-wave', 'sxt', 'shimano', 'kenda']):
                brand = product.get('producator', '').lower()
                if brand and brand.replace('-', '').replace(' ', '') in filename_clean.replace('-', '').replace(' ', ''):
                    score += 0.2
            
            if score > best_score and score > 0.25:  # Lower threshold for better matching
                best_score = score
                best_match = product
                
        return best_match
    
    def generate_product_catalog(self) -> Dict:
        """Generate the complete product catalog."""
        print("🔄 Parsing CSV product data...")
        products_data = self.parse_csv_data()
        print(f"📊 Found {len(products_data)} products in CSV")
        
        print("🔄 Parsing sitemap URLs...")
        urls = self.parse_sitemap_urls()
        print(f"🔗 Found {len(urls)} URLs in sitemap")
        
        products = []
        categories_count = {}
        brands_count = {}
        
        print("🔄 Matching URLs to products...")
        matched_count = 0
        
        # Process ALL products from the CSV (not just a sample)
        all_unique_products = {}
        for product_data in products_data.values():
            if not product_data.get('nume_produs'):
                continue
            # Use product code as key to avoid duplicates
            key = product_data.get('cod_produs', product_data.get('nume_produs', ''))
            if key and key not in all_unique_products:
                all_unique_products[key] = product_data
        
        sample_products = list(all_unique_products.values())  # All unique products
        print(f"📊 Processing {len(sample_products)} unique products...")
        
        # Create URL-to-product mapping for better matching
        url_mappings = {}
        for url in urls:
            matched_product = self.match_url_to_product(url, products_data)
            if matched_product:
                url_mappings[matched_product.get('cod_produs', '')] = url
        
        print(f"🔗 Successfully mapped {len(url_mappings)} URLs to products")
        
        for i, product_data in enumerate(sample_products):
            if not product_data.get('nume_produs'):
                continue
                
            # Create product ID
            name = product_data['nume_produs']
            product_id = re.sub(r'[^\w\s-]', '', name.lower()).replace(' ', '-')[:60]
            
            # Extract brand
            brand = self.extract_brand_from_name(name)
            brands_count[brand] = brands_count.get(brand, 0) + 1
            
            # Determine category
            category = self.extract_category_from_url(product_data.get('categorie_path', ''))
            if 'biciclet' in product_data.get('nume_categorie', '').lower():
                category = 'biciclete'
            elif 'anvelop' in name.lower() or 'camera' in name.lower():
                category = 'piese-schimb'
                
            categories_count[category] = categories_count.get(category, 0) + 1
            
            # Process images
            images = []
            if product_data.get('imag_baza'):
                images.append(product_data['imag_baza'])
            
            if product_data.get('imag_galerie'):
                gallery_images = product_data['imag_galerie'].split('|')
                images.extend(gallery_images[:3])  # Max 3 additional images
            
            # Calculate discount
            selling_price = product_data.get('pret_sugerat', 0)  # Price we show to customers
            cost_price = product_data.get('pret_produs', 0)      # Purchase/cost price
            discount_percent = 0
            # For display purposes, we can show a discount from a higher "original" price
            if selling_price and cost_price and selling_price > cost_price:
                # Create a fictional "original price" that's higher than selling price for discount display
                fictional_original = selling_price * 1.5  # 50% markup for display
                discount_percent = round(((fictional_original - selling_price) / fictional_original) * 100, 2)
            
            # Build product object
            product = {
                'id': product_id,
                'name': name,
                'brand': brand,
                'category': category,
                'price': selling_price,  # Use pret_sugerat (selling price)
                'currency': 'RON',
                'availability': 'in_stock' if product_data.get('in_stock') else 'out_of_stock',
                'stock_quantity': product_data.get('cant_stock', 0),
                'sku': product_data.get('cod_produs', ''),
                'ean': product_data.get('cod_ean', ''),
                'description': product_data.get('descriere', ''),
                'url': url_mappings.get(product_data.get('cod_produs', ''), ''),  # Add URL from mapping
                'images': images,
                'rating': round(4.0 + (i % 10) * 0.1, 1),  # Simulated ratings 4.0-4.9
                'reviews_count': (i % 50) + 1,  # Simulated review counts
                'warranty': '12 luni' if selling_price < 100 else '24 luni',
                'tags': [category.replace('-', ' '), brand.lower()],
                'scraped_at': datetime.now().isoformat()
            }
            
            # Add discount info if applicable
            if discount_percent > 0:
                fictional_original = selling_price * 1.5
                product['original_price'] = fictional_original
                product['discount_percent'] = discount_percent
            
            # Add weight if available
            if product_data.get('greutate'):
                try:
                    weight = float(product_data['greutate'])
                    product['weight'] = f"{weight} kg"
                except:
                    pass
            
            products.append(product)
            matched_count += 1
        
        print(f"✅ Successfully processed {matched_count} products")
        
        # Build category structure
        categories = []
        for cat_id, count in categories_count.items():
            cat_name = {
                'biciclete': 'Biciclete',
                'accesorii': 'Accesorii',
                'piese-schimb': 'Piese de Schimb'
            }.get(cat_id, cat_id.title())
            
            categories.append({
                'id': cat_id,
                'name': cat_name,
                'count': count
            })
        
        # Build brand structure
        brands = []
        for brand_name, count in sorted(brands_count.items(), key=lambda x: x[1], reverse=True):
            brands.append({
                'name': brand_name,
                'product_count': count
            })
        
        # Build final catalog
        catalog = {
            'last_updated': datetime.now().isoformat(),
            'total_products': len(products),
            'version': '2.0.0',
            'source': 'bikestylish.ro',
            'categories': categories,
            'brands': brands[:20],  # Top 20 brands
            'products': products,
            'api_info': {
                'version': '2.0',
                'endpoints': [
                    '/data/products.json',
                    '/data/categories.json', 
                    '/data/brands.json'
                ],
                'rate_limit': 'No limit (static JSON)',
                'cors': 'Enabled',
                'cache_ttl': '24 hours'
            },
            'metadata': {
                'scraper_version': '2.0.0',
                'products_scraped': len(products),
                'csv_products_total': len(products_data),
                'sitemap_urls_total': len(urls),
                'last_update_source': 'CSV + Sitemap parsing'
            }
        }
        
        return catalog

def main():
    """Main execution function."""
    parser = BikeStylishDataParser()
    
    try:
        print("🚀 Starting BikeStylish real data parsing...")
        catalog = parser.generate_product_catalog()
        
        # Save to JSON file
        output_file = '../data/products.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Successfully created catalog with:")
        print(f"   📦 {catalog['total_products']} products")
        print(f"   🏷️ {len(catalog['categories'])} categories") 
        print(f"   🏭 {len(catalog['brands'])} brands")
        print(f"   💾 Saved to: {output_file}")
        
        # Display sample products
        print(f"\n📋 Sample products:")
        for i, product in enumerate(catalog['products'][:5]):
            print(f"   {i+1}. {product['name']} - {product['price']} RON ({product['brand']})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
