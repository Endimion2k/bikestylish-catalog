#!/usr/bin/env python3
"""
Extract categories from URL structure in link.txt
"""

import re
from collections import defaultdict
import xml.etree.ElementTree as ET

def extract_url_categories():
    """Extract all categories from URLs in link.txt"""
    
    print("🔗 Extracting categories from URL structure...")
    
    # Parse XML sitemap
    try:
        tree = ET.parse('../../link.txt')
        root = tree.getroot()
        
        # Define namespace
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Extract all URLs
        urls = []
        for url_elem in root.findall('ns:url', ns):
            loc_elem = url_elem.find('ns:loc', ns)
            if loc_elem is not None:
                urls.append(loc_elem.text.strip())
        
        print(f"📦 Found {len(urls)} URLs in sitemap")
        
    except Exception as e:
        print(f"❌ Error parsing XML: {e}")
        
        # Fallback: read as text and extract URLs with regex
        with open('../../link.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract URLs from CDATA sections
        url_pattern = r'https://www\.bikestylish\.ro/([^/]+)/([^\.]+)\.html'
        matches = re.findall(url_pattern, content)
        
        urls = [f"https://www.bikestylish.ro/{cat}/{prod}.html" for cat, prod in matches]
        print(f"📦 Found {len(urls)} URLs via regex")
    
    # Extract categories from URLs
    url_categories = defaultdict(list)
    category_counts = defaultdict(int)
    
    url_pattern = r'bikestylish\.ro/([^/]+)/'
    
    for url in urls:
        match = re.search(url_pattern, url)
        if match:
            category = match.group(1)
            category_counts[category] += 1
            
            # Extract product name
            product_match = re.search(r'/([^/]+)\.html$', url)
            if product_match:
                product_name = product_match.group(1).replace('-', ' ')
                url_categories[category].append(product_name)
    
    print(f"\n📊 URL Categories found:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: {count:,} products")
    
    # Analyze products in each category to understand mapping patterns
    print(f"\n🔍 Sample products per category:")
    
    for category in sorted(category_counts.keys()):
        sample_products = url_categories[category][:10]  # First 10 products
        print(f"\n📂 {category} ({category_counts[category]:,} products):")
        
        for i, product in enumerate(sample_products, 1):
            print(f"   {i}. {product[:80]}...")
        
        # Identify common keywords in this category
        all_words = []
        for product in url_categories[category][:50]:  # Analyze first 50 products
            words = product.lower().split()
            all_words.extend(words)
        
        # Count word frequency
        word_counts = defaultdict(int)
        for word in all_words:
            if len(word) > 2:  # Skip short words
                word_counts[word] += 1
        
        # Show top keywords
        top_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_keywords:
            print(f"   🔑 Top keywords: {', '.join([f'{word}({count})' for word, count in top_keywords])}")
    
    return url_categories, category_counts

def suggest_improved_mapping():
    """Suggest improved category mapping based on URL analysis"""
    
    url_categories, category_counts = extract_url_categories()
    
    print(f"\n💡 Suggested category mapping improvements:")
    
    # Map URL categories to our category structure
    url_to_category_mapping = {
        'piese': {
            'description': 'Parts and components - main technical products',
            'suggested_categories': [
                'anvelope', 'camere-de-bicicleta', 'jante', 'roti-fata', 'roti-spate',
                'pedale', 'lanturi', 'pinioane', 'angrenaje', 'frane-v-brake',
                'placute-frana-disc', 'saboti-frana', 'disc-frana', 'ghidoane',
                'mansoane', 'ghidoline', 'pipe-ghidon', 'tije-ghidon', 'șei',
                'tije-șa-49', 'lumini', 'lumini-fata', 'lumini-spate'
            ]
        },
        'accesorii-bicicleta': {
            'description': 'Bicycle accessories - additional equipment',
            'suggested_categories': [
                'antifurturi', 'cosuri-pentru-biciclete', 'scaune-pentru-copii',
                'roti-ajutatoare', 'aparatori-noroi', 'suport-bidon-si-bidon',
                'reflectorizante', 'accesorii', 'protectii-cadru'
            ]
        },
        'scule-si-intretinere': {
            'description': 'Tools and maintenance',
            'suggested_categories': [
                'pompe', 'scule-si-intretinere', 'truse-de-scule', 'cabluri'
            ]
        }
    }
    
    for url_cat, info in url_to_category_mapping.items():
        count = category_counts.get(url_cat, 0)
        print(f"\n🏷️ {url_cat} ({count:,} products)")
        print(f"   Description: {info['description']}")
        print(f"   Suggested categories: {', '.join(info['suggested_categories'])}")
    
    return url_to_category_mapping

if __name__ == "__main__":
    suggest_improved_mapping()
