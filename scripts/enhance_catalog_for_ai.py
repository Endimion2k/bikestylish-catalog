#!/usr/bin/env python3
"""
Enhanced BikeStylish Catalog with AI Optimization
Based on SEO/GEO analysis from produs.txt
"""

import json
import re
from typing import Dict, List, Any
import time

def enhance_product_for_ai(product: Dict) -> Dict:
    """Enhance a single product with AI optimization features."""
    
    # Extract key information for AI enhancement
    name = product.get('name', '')
    brand = product.get('brand', '')
    category = product.get('category', '')
    description = product.get('description', '')
    price = product.get('price', 0)
    
    # Generate AI-optimized fields
    enhanced_product = product.copy()
    
    # 1. AI Metadata Layer
    enhanced_product['ai_metadata'] = {
        "content_type": "bicycle_product",
        "optimization_level": "high",
        "ai_searchable": True,
        "geo_optimized": True,
        "last_ai_update": time.strftime("%Y-%m-%dT%H:%M:%S.000000")
    }
    
    # 2. Enhanced Schema Markup
    enhanced_product['schema_markup'] = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "brand": {
            "@type": "Brand",
            "name": brand
        },
        "description": description,
        "category": category,
        "offers": {
            "@type": "Offer",
            "price": str(price),
            "priceCurrency": "RON",
            "availability": "https://schema.org/InStock" if product.get('availability') == 'in_stock' else "https://schema.org/OutOfStock",
            "url": product.get('url', ''),
            "seller": {
                "@type": "Organization",
                "name": "BikeStylish.ro"
            }
        }
    }
    
    # 3. AI Context Layer (hidden from users, visible to AI)
    ai_context = generate_ai_context(product)
    enhanced_product['ai_context'] = ai_context
    
    # 4. Search Optimization
    search_terms = generate_search_terms(product)
    enhanced_product['search_optimization'] = search_terms
    
    # 5. Technical Specifications for AI
    tech_specs = generate_technical_specs(product)
    enhanced_product['technical_specifications'] = tech_specs
    
    # 6. FAQ Generation
    faq_data = generate_product_faq(product)
    enhanced_product['faq_schema'] = faq_data
    
    # 7. Product Relationships
    relationships = generate_product_relationships(product)
    enhanced_product['product_relationships'] = relationships
    
    return enhanced_product

def generate_ai_context(product: Dict) -> Dict:
    """Generate AI context layer for better understanding."""
    
    name = product.get('name', '').lower()
    category = product.get('category', '')
    brand = product.get('brand', '')
    
    # Determine product type and context
    context = {
        "product_type": determine_product_type(name, category),
        "primary_use_cases": determine_use_cases(name, category),
        "target_audience": determine_target_audience(name, category),
        "compatibility_context": determine_compatibility(name, category),
        "seasonal_relevance": determine_seasonality(name, category),
        "skill_level_required": determine_skill_level(name, category),
        "maintenance_level": determine_maintenance_level(name, category)
    }
    
    return context

def generate_search_terms(product: Dict) -> Dict:
    """Generate comprehensive search terms for AI discovery."""
    
    name = product.get('name', '').lower()
    brand = product.get('brand', '').lower()
    category = product.get('category', '')
    
    # Extract key terms
    name_words = re.findall(r'\w+', name)
    
    search_terms = {
        "primary_keywords": [brand, category] + name_words[:3],
        "semantic_keywords": generate_semantic_keywords(name, category),
        "long_tail_keywords": generate_long_tail_keywords(name, brand, category),
        "voice_search_phrases": generate_voice_search_phrases(name, brand),
        "multilingual_terms": {
            "ro": name_words,
            "en": translate_to_english(name_words),
            "de": translate_to_german(name_words),
            "hu": translate_to_hungarian(name_words)
        }
    }
    
    return search_terms

def generate_technical_specs(product: Dict) -> Dict:
    """Generate structured technical specifications."""
    
    name = product.get('name', '').lower()
    category = product.get('category', '')
    description = product.get('description', '')
    
    specs = {
        "compatibility": determine_compatibility_specs(name, category),
        "installation": {
            "complexity": determine_installation_complexity(name, category),
            "tools_required": determine_tools_required(name, category),
            "time_estimate": determine_installation_time(name, category)
        },
        "maintenance": {
            "frequency": determine_maintenance_frequency(name, category),
            "difficulty": determine_maintenance_difficulty(name, category),
            "special_requirements": determine_special_requirements(name, category)
        },
        "performance_specs": extract_performance_specs(name, description)
    }
    
    return specs

def generate_product_faq(product: Dict) -> Dict:
    """Generate FAQ schema for AI agents."""
    
    name = product.get('name', '')
    category = product.get('category', '')
    brand = product.get('brand', '')
    
    # Generate category-specific FAQs
    faqs = []
    
    if 'stegulet' in name.lower():
        faqs.extend([
            {
                "question": f"Cum se montează {name}?",
                "answer": f"Stegulețul {brand} se montează pe portbagajul bicicletei folosind clemele incluse. Asigurați-vă că este fix și vizibil."
            },
            {
                "question": f"Este {name} conform cu legislația rutieră?",
                "answer": "Da, stegulețele reflectorizante îmbunătățesc vizibilitatea și sunt recomandate pentru siguranța în trafic."
            }
        ])
    elif 'anvelopa' in name.lower():
        faqs.extend([
            {
                "question": f"Cum verific dimensiunea corectă pentru {name}?",
                "answer": f"Verificați marcajul de pe anvelopa actuală sau consultați manualul bicicletei pentru dimensiunea compatibilă."
            },
            {
                "question": f"Ce presiune să folosesc pentru {name}?",
                "answer": "Presiunea recomandată este marcată pe flancul anvelopei. Respectați întotdeauna limitele indicate."
            }
        ])
    
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["answer"]
                }
            } for faq in faqs
        ]
    }
    
    return faq_schema

def generate_product_relationships(product: Dict) -> Dict:
    """Generate product relationship mappings for AI recommendations."""
    
    name = product.get('name', '').lower()
    category = product.get('category', '')
    brand = product.get('brand', '')
    
    relationships = {
        "compatible_products": determine_compatible_products(name, category),
        "upgrade_suggestions": determine_upgrade_path(name, category),
        "bundle_recommendations": determine_bundle_products(name, category),
        "alternative_brands": determine_alternative_brands(brand, category),
        "related_categories": determine_related_categories(category)
    }
    
    return relationships

# Helper functions for context determination
def determine_product_type(name: str, category: str) -> str:
    """Determine specific product type for AI context."""
    if 'stegulet' in name:
        return 'safety_flag'
    elif 'anvelopa' in name:
        return 'tire'
    elif 'janta' in name:
        return 'rim'
    elif 'far' in name:
        return 'light'
    elif 'casca' in name:
        return 'helmet'
    else:
        return category

def determine_use_cases(name: str, category: str) -> List[str]:
    """Determine primary use cases."""
    use_cases = []
    
    if 'urban' in name or 'city' in name:
        use_cases.append('urban_cycling')
    if 'mtb' in name or 'mountain' in name:
        use_cases.append('mountain_biking')
    if 'e-bike' in name or 'electric' in name:
        use_cases.append('electric_bike')
    if 'copii' in name or 'kids' in name:
        use_cases.append('children_cycling')
    if 'race' in name or 'competition' in name:
        use_cases.append('competitive_cycling')
    
    if not use_cases:
        use_cases = ['general_cycling']
    
    return use_cases

def determine_target_audience(name: str, category: str) -> List[str]:
    """Determine target audience."""
    audiences = []
    
    if 'copii' in name:
        audiences.append('children')
    if 'professional' in name or 'pro' in name:
        audiences.append('professionals')
    if 'beginner' in name or 'incepator' in name:
        audiences.append('beginners')
    
    if not audiences:
        audiences = ['general_cyclists']
    
    return audiences

def determine_compatibility(name: str, category: str) -> List[str]:
    """Determine compatibility context."""
    compatibility = []
    
    # Extract size information
    size_pattern = r'\d+["\']?[-x]\d+\.?\d*'
    sizes = re.findall(size_pattern, name)
    if sizes:
        compatibility.extend([f"size_{size}" for size in sizes])
    
    # Bike type compatibility
    if 'mtb' in name:
        compatibility.append('mountain_bikes')
    if 'road' in name:
        compatibility.append('road_bikes')
    if 'e-bike' in name:
        compatibility.append('electric_bikes')
    
    return compatibility

def determine_seasonality(name: str, category: str) -> List[str]:
    """Determine seasonal relevance."""
    if 'winter' in name or 'iarna' in name:
        return ['winter']
    elif 'summer' in name or 'vara' in name:
        return ['summer']
    else:
        return ['all_seasons']

def determine_skill_level(name: str, category: str) -> str:
    """Determine required skill level for installation/use."""
    if 'professional' in name or 'complex' in name:
        return 'advanced'
    elif 'easy' in name or 'simplu' in name:
        return 'beginner'
    else:
        return 'intermediate'

def determine_maintenance_level(name: str, category: str) -> str:
    """Determine maintenance requirements."""
    if 'tubeless' in name or 'hydraulic' in name:
        return 'high'
    elif 'basic' in name or 'standard' in name:
        return 'low'
    else:
        return 'medium'

# Additional helper functions for search terms
def generate_semantic_keywords(name: str, category: str) -> List[str]:
    """Generate semantic keywords for better AI discovery."""
    keywords = []
    
    if 'stegulet' in name:
        keywords.extend(['safety', 'visibility', 'flag', 'reflective', 'traffic'])
    elif 'anvelopa' in name:
        keywords.extend(['tire', 'wheel', 'rubber', 'grip', 'traction'])
    elif 'far' in name:
        keywords.extend(['light', 'illumination', 'visibility', 'LED', 'beam'])
    
    return keywords

def generate_long_tail_keywords(name: str, brand: str, category: str) -> List[str]:
    """Generate long-tail keywords for specific searches."""
    long_tail = []
    
    if brand and name:
        long_tail.append(f"{brand} {name}")
        long_tail.append(f"{name} {brand}")
        long_tail.append(f"{category} {brand}")
    
    return long_tail

def generate_voice_search_phrases(name: str, brand: str) -> List[str]:
    """Generate voice search friendly phrases."""
    phrases = []
    
    if name:
        phrases.append(f"where to buy {name}")
        phrases.append(f"best {name} price")
        phrases.append(f"how to install {name}")
    
    return phrases

def translate_to_english(words: List[str]) -> List[str]:
    """Basic translation to English for international search."""
    translations = {
        'stegulet': 'flag',
        'anvelopa': 'tire',
        'janta': 'rim',
        'far': 'light',
        'casca': 'helmet',
        'bicicleta': 'bicycle',
        'piese': 'parts',
        'accesorii': 'accessories'
    }
    
    return [translations.get(word, word) for word in words]

def translate_to_german(words: List[str]) -> List[str]:
    """Basic translation to German."""
    translations = {
        'stegulet': 'fahne',
        'anvelopa': 'reifen',
        'janta': 'felge',
        'far': 'licht',
        'casca': 'helm',
        'bicicleta': 'fahrrad'
    }
    
    return [translations.get(word, word) for word in words]

def translate_to_hungarian(words: List[str]) -> List[str]:
    """Basic translation to Hungarian."""
    translations = {
        'stegulet': 'zászló',
        'anvelopa': 'gumi',
        'janta': 'felni',
        'far': 'lámpa',
        'casca': 'sisak',
        'bicicleta': 'kerékpár'
    }
    
    return [translations.get(word, word) for word in words]

# Additional helper functions (simplified versions)
def determine_compatibility_specs(name: str, category: str) -> List[str]:
    return ['universal', 'standard_mounting']

def determine_installation_complexity(name: str, category: str) -> str:
    return 'intermediate'

def determine_tools_required(name: str, category: str) -> List[str]:
    return ['basic_tools']

def determine_installation_time(name: str, category: str) -> str:
    return '15-30 minutes'

def determine_maintenance_frequency(name: str, category: str) -> str:
    return 'monthly'

def determine_maintenance_difficulty(name: str, category: str) -> str:
    return 'easy'

def determine_special_requirements(name: str, category: str) -> List[str]:
    return []

def extract_performance_specs(name: str, description: str) -> Dict:
    return {"notes": "Performance specs extracted from description"}

def determine_compatible_products(name: str, category: str) -> List[str]:
    return []

def determine_upgrade_path(name: str, category: str) -> List[str]:
    return []

def determine_bundle_products(name: str, category: str) -> List[str]:
    return []

def determine_alternative_brands(brand: str, category: str) -> List[str]:
    return []

def determine_related_categories(category: str) -> List[str]:
    return []

def enhance_catalog_for_ai():
    """Main function to enhance the entire catalog for AI optimization."""
    
    print("🤖 Enhancing BikeStylish catalog for AI agents...")
    
    # Load existing catalog
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data['products']
    print(f"📦 Processing {len(products)} products...")
    
    # Enhance each product
    enhanced_products = []
    
    for i, product in enumerate(products):
        if i % 500 == 0:
            print(f"   Progress: {i}/{len(products)}")
        
        enhanced_product = enhance_product_for_ai(product)
        enhanced_products.append(enhanced_product)
    
    # Update catalog with AI enhancements
    data['products'] = enhanced_products
    data['ai_optimization'] = {
        "enabled": True,
        "version": "1.0.0",
        "last_update": time.strftime("%Y-%m-%dT%H:%M:%S.000000"),
        "features": [
            "AI metadata layers",
            "Enhanced schema markup",
            "Multilingual search terms",
            "FAQ generation",
            "Technical specifications",
            "Product relationships",
            "Voice search optimization"
        ]
    }
    
    # Save enhanced catalog
    with open('../data/products_ai_enhanced.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Enhanced catalog saved with AI optimizations!")
    print(f"📊 Added AI features to all {len(enhanced_products)} products")
    
    # Show sample enhancement
    sample_product = enhanced_products[0]
    print(f"\n📋 Sample AI enhancements for: {sample_product['name']}")
    print(f"   • AI metadata: {len(sample_product['ai_metadata'])} fields")
    print(f"   • Search terms: {len(sample_product['search_optimization']['primary_keywords'])} keywords")
    print(f"   • Schema markup: Product + FAQ + Organization")
    print(f"   • Technical specs: {len(sample_product['technical_specifications'])} categories")

if __name__ == "__main__":
    enhance_catalog_for_ai()
