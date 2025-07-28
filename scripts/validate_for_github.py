#!/usr/bin/env python3
"""
Pre-upload repository validation for GitHub
"""

import os
import json
import sys
from pathlib import Path

def validate_repository():
    """Validate repository structure before GitHub upload."""
    
    print("🔍 Validating BikeStylish repository for GitHub upload...")
    
    # Check repository root
    repo_path = Path("..").resolve()
    print(f"📁 Repository path: {repo_path}")
    
    # Required files
    required_files = [
        "README.md",
        "LICENSE", 
        ".gitignore",
        ".gitattributes",
        "requirements.txt",
        "data/products.json",
        "data/products_ai_enhanced.json",
        "AI_OPTIMIZATION_GUIDE.md",
        "GITHUB_UPLOAD_GUIDE.md"
    ]
    
    print("\n✅ Checking required files...")
    missing_files = []
    
    for file in required_files:
        file_path = repo_path / file
        if file_path.exists():
            size = file_path.stat().st_size
            size_mb = size / (1024 * 1024)
            print(f"   ✅ {file} ({size_mb:.1f} MB)")
            
            # Check GitHub file size limits
            if size_mb > 100:
                print(f"   ⚠️  WARNING: {file} is {size_mb:.1f}MB (GitHub limit: 100MB)")
                print(f"      Consider using Git LFS for this file")
        else:
            missing_files.append(file)
            print(f"   ❌ MISSING: {file}")
    
    # Validate JSON files
    print("\n✅ Validating JSON files...")
    
    json_files = [
        "data/products.json",
        "data/products_ai_enhanced.json", 
        "data/brands.json",
        "data/categories.json"
    ]
    
    for json_file in json_files:
        json_path = repo_path / json_file
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if json_file.endswith('products.json') or json_file.endswith('products_ai_enhanced.json'):
                    product_count = len(data.get('products', []))
                    print(f"   ✅ {json_file}: {product_count} products")
                    
                    # Check AI enhancements
                    if 'ai_enhanced' in json_file:
                        sample_product = data['products'][0] if data['products'] else {}
                        ai_features = []
                        if 'ai_metadata' in sample_product:
                            ai_features.append('ai_metadata')
                        if 'ai_context' in sample_product:
                            ai_features.append('ai_context')
                        if 'search_optimization' in sample_product:
                            ai_features.append('search_optimization')
                        if 'faq_schema' in sample_product:
                            ai_features.append('faq_schema')
                        
                        print(f"      🤖 AI features: {', '.join(ai_features)}")
                else:
                    items = len(data) if isinstance(data, list) else len(data.keys())
                    print(f"   ✅ {json_file}: {items} items")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ INVALID JSON: {json_file} - {e}")
        else:
            print(f"   ❌ MISSING: {json_file}")
    
    # Check folder structure
    print("\n✅ Checking folder structure...")
    
    required_folders = [
        "data",
        "scripts", 
        ".github/workflows"
    ]
    
    for folder in required_folders:
        folder_path = repo_path / folder
        if folder_path.exists() and folder_path.is_dir():
            file_count = len(list(folder_path.glob("*")))
            print(f"   ✅ {folder}/ ({file_count} files)")
        else:
            print(f"   ❌ MISSING: {folder}/")
    
    # Generate repository stats
    print("\n📊 Repository Statistics:")
    
    try:
        with open(repo_path / "data/products.json", 'r', encoding='utf-8') as f:
            products_data = json.load(f)
            
        total_products = len(products_data.get('products', []))
        brands = len(products_data.get('brands', []))
        categories = len(products_data.get('categories', []))
        
        # Count products with URLs
        products_with_urls = len([p for p in products_data['products'] if p.get('url')])
        url_coverage = (products_with_urls / total_products * 100) if total_products > 0 else 0
        
        print(f"   📦 Total products: {total_products:,}")
        print(f"   🏷️  Brands: {brands}")
        print(f"   📂 Categories: {categories}")
        print(f"   🔗 URL coverage: {url_coverage:.1f}% ({products_with_urls:,} products)")
        
        # Check AI enhancement coverage
        try:
            with open(repo_path / "data/products_ai_enhanced.json", 'r', encoding='utf-8') as f:
                ai_data = json.load(f)
                
            ai_products = len(ai_data.get('products', []))
            sample_ai_product = ai_data['products'][0] if ai_data['products'] else {}
            
            ai_features_count = 0
            if 'ai_metadata' in sample_ai_product:
                ai_features_count += 1
            if 'ai_context' in sample_ai_product:
                ai_features_count += 1
            if 'search_optimization' in sample_ai_product:
                ai_features_count += 1
            if 'technical_specifications' in sample_ai_product:
                ai_features_count += 1
            if 'faq_schema' in sample_ai_product:
                ai_features_count += 1
                
            print(f"   🤖 AI-enhanced products: {ai_products:,}")
            print(f"   🧠 AI features per product: {ai_features_count}")
            
        except Exception as e:
            print(f"   ❌ Error reading AI-enhanced data: {e}")
        
    except Exception as e:
        print(f"   ❌ Error reading products data: {e}")
    
    # Final validation
    print("\n🎯 Final Validation:")
    
    if missing_files:
        print(f"   ❌ Missing {len(missing_files)} required files")
        for file in missing_files:
            print(f"      - {file}")
        return False
    else:
        print("   ✅ All required files present")
    
    # Calculate total size
    total_size = 0
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if not file.startswith('.git'):
                file_path = Path(root) / file
                total_size += file_path.stat().st_size
    
    total_size_mb = total_size / (1024 * 1024)
    print(f"   📊 Total repository size: {total_size_mb:.1f} MB")
    
    if total_size_mb > 1000:  # 1GB warning
        print(f"   ⚠️  WARNING: Repository is quite large ({total_size_mb:.1f}MB)")
        print(f"      Consider using Git LFS for large files")
    
    print("\n🚀 Repository is ready for GitHub upload!")
    
    # Generate GitHub URLs preview
    print("\n🌐 Expected GitHub URLs:")
    username = "[YOUR_USERNAME]"
    repo_name = "bikestylish-catalog"
    
    print(f"   📋 Repository: https://github.com/{username}/{repo_name}")
    print(f"   📊 API Endpoint: https://raw.githubusercontent.com/{username}/{repo_name}/main/data/products.json")
    print(f"   🤖 AI Enhanced API: https://raw.githubusercontent.com/{username}/{repo_name}/main/data/products_ai_enhanced.json")
    print(f"   📖 Documentation: https://github.com/{username}/{repo_name}#readme")
    
    return True

if __name__ == "__main__":
    try:
        success = validate_repository()
        if success:
            print("\n✅ VALIDATION PASSED - Ready for GitHub upload!")
            sys.exit(0)
        else:
            print("\n❌ VALIDATION FAILED - Please fix issues before upload")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 VALIDATION ERROR: {e}")
        sys.exit(1)
