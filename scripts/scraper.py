#!/usr/bin/env python3
"""
BikeStylish.ro Product Scraper

This script scrapes product data from BikeStylish.ro and generates
a JSON catalog for AI agent consumption.
"""

import requests
import json
import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class BikeStylishScraper:
    def __init__(self):
        self.base_url = "https://bikestylish.ro"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.products = []
        self.categories = []
        self.brands = set()
        
    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page with retry logic."""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logging.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
    
    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text string."""
        if not text:
            return None
        
        # Remove currency symbols and clean text
        price_text = re.sub(r'[^\d,.\s]', '', text.strip())
        # Handle Romanian decimal separator
        price_text = price_text.replace(',', '.')
        
        # Extract numeric value
        price_match = re.search(r'(\d+(?:\.\d{2})?)', price_text)
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                return None
        return None
    
    def scrape_categories(self) -> List[Dict]:
        """Scrape product categories from the main navigation."""
        logging.info("Scraping categories...")
        
        soup = self.get_page(self.base_url)
        if not soup:
            return []
        
        categories = []
        
        # Look for navigation menu or category links
        nav_selectors = [
            '.main-navigation .menu-item',
            '.category-menu a',
            '.nav-categories a',
            'nav a[href*="categori"]'
        ]
        
        for selector in nav_selectors:
            nav_items = soup.select(selector)
            if nav_items:
                for item in nav_items:
                    href = item.get('href', '')
                    text = item.get_text(strip=True)
                    
                    if text and 'biciclet' in text.lower() or 'accesor' in text.lower():
                        category_id = re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))
                        categories.append({
                            'id': category_id,
                            'name': text,
                            'url': urljoin(self.base_url, href),
                            'count': 0  # Will be updated during product scraping
                        })
                break
        
        # Fallback: default categories
        if not categories:
            categories = [
                {'id': 'biciclete', 'name': 'Biciclete', 'url': f"{self.base_url}/biciclete", 'count': 0},
                {'id': 'accesorii', 'name': 'Accesorii', 'url': f"{self.base_url}/accesorii", 'count': 0},
                {'id': 'piese-schimb', 'name': 'Piese de Schimb', 'url': f"{self.base_url}/piese-schimb", 'count': 0}
            ]
        
        logging.info(f"Found {len(categories)} categories")
        return categories
    
    def scrape_product_list(self, category_url: str, max_pages: int = 5) -> List[str]:
        """Scrape product URLs from category pages."""
        product_urls = []
        
        for page in range(1, max_pages + 1):
            page_url = f"{category_url}?page={page}"
            soup = self.get_page(page_url)
            
            if not soup:
                break
            
            # Common product link selectors for e-commerce sites
            product_selectors = [
                '.product-item a',
                '.product-card a',
                '.product-link',
                'a[href*="/produs/"]',
                'a[href*="/product/"]',
                '.item-product a'
            ]
            
            page_products = []
            for selector in product_selectors:
                links = soup.select(selector)
                if links:
                    for link in links:
                        href = link.get('href')
                        if href:
                            full_url = urljoin(self.base_url, href)
                            if full_url not in product_urls:
                                page_products.append(full_url)
                    break
            
            if not page_products:
                # No products found on this page, might be end of pagination
                break
                
            product_urls.extend(page_products)
            logging.info(f"Found {len(page_products)} products on page {page}")
            
            # Rate limiting
            time.sleep(1)
        
        return product_urls
    
    def scrape_product_details(self, product_url: str) -> Optional[Dict]:
        """Scrape detailed product information."""
        soup = self.get_page(product_url)
        if not soup:
            return None
        
        try:
            # Extract basic product info
            title_selectors = ['h1.product-title', 'h1', '.product-name h1', '.product-title']
            title = None
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title:
                logging.warning(f"No title found for {product_url}")
                return None
            
            # Extract price
            price_selectors = ['.price', '.product-price', '.current-price', '.price-current']
            price = None
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price = self.extract_price(price_elem.get_text())
                    if price:
                        break
            
            # Extract brand from title or dedicated field
            brand = "Unknown"
            for brand_name in ["Cross", "Giant", "Trek", "Specialized", "Scott", "Merida", "Cannondale"]:
                if brand_name.lower() in title.lower():
                    brand = brand_name
                    break
            
            # Extract description
            desc_selectors = ['.product-description', '.description', '.product-details']
            description = ""
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)[:500]  # Limit length
                    break
            
            # Extract images
            img_selectors = ['.product-images img', '.product-gallery img', '.product-image img']
            images = []
            for selector in img_selectors:
                img_elements = soup.select(selector)
                for img in img_elements[:3]:  # Limit to 3 images
                    src = img.get('src') or img.get('data-src')
                    if src:
                        images.append(urljoin(self.base_url, src))
                if images:
                    break
            
            # Generate product ID from URL
            product_id = re.sub(r'[^a-z0-9-]', '', title.lower().replace(' ', '-'))[:50]
            
            # Build product object
            product = {
                'id': product_id,
                'name': title,
                'brand': brand,
                'category': 'biciclete',  # Default, will be updated based on URL
                'price': price or 0.0,
                'currency': 'RON',
                'availability': 'in_stock',
                'description': description,
                'url': product_url,
                'images': images,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Add brand to set
            self.brands.add(brand)
            
            return product
            
        except Exception as e:
            logging.error(f"Error scraping product {product_url}: {e}")
            return None
    
    def run_scraper(self, max_products_per_category: int = 50) -> Dict:
        """Run the complete scraping process."""
        logging.info("Starting BikeStylish.ro scraping...")
        
        # Scrape categories
        categories = self.scrape_categories()
        
        # Scrape products from each category
        all_products = []
        
        for category in categories:
            logging.info(f"Scraping category: {category['name']}")
            
            # Get product URLs
            product_urls = self.scrape_product_list(
                category['url'], 
                max_pages=max_products_per_category // 20
            )
            
            # Limit products per category
            product_urls = product_urls[:max_products_per_category]
            
            category_products = []
            for url in product_urls:
                product = self.scrape_product_details(url)
                if product:
                    product['category'] = category['id']
                    category_products.append(product)
                    all_products.append(product)
                
                # Rate limiting
                time.sleep(0.5)
            
            # Update category count
            category['count'] = len(category_products)
            logging.info(f"Scraped {len(category_products)} products from {category['name']}")
        
        # Build final catalog
        catalog = {
            'last_updated': datetime.now().isoformat(),
            'total_products': len(all_products),
            'version': '1.0.0',
            'source': 'bikestylish.ro',
            'categories': categories,
            'brands': [{'name': brand, 'product_count': 0} for brand in sorted(self.brands)],
            'products': all_products,
            'metadata': {
                'scraper_version': '1.0.0',
                'last_scrape_duration': 'Unknown',
                'products_scraped': len(all_products)
            }
        }
        
        # Update brand counts
        for brand_info in catalog['brands']:
            brand_info['product_count'] = sum(
                1 for p in all_products if p['brand'] == brand_info['name']
            )
        
        logging.info(f"Scraping completed. Total products: {len(all_products)}")
        return catalog

def main():
    """Main scraper execution."""
    scraper = BikeStylishScraper()
    
    try:
        catalog = scraper.run_scraper(max_products_per_category=20)
        
        # Save catalog to JSON
        output_file = '../data/products.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Catalog saved to {output_file}")
        print(f"✅ Successfully scraped {catalog['total_products']} products")
        print(f"📁 Catalog saved to {output_file}")
        
    except Exception as e:
        logging.error(f"Scraper failed: {e}")
        print(f"❌ Scraping failed: {e}")

if __name__ == "__main__":
    main()
