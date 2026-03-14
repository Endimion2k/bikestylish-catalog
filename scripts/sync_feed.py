#!/usr/bin/env python3
"""
BikeStylish Catalog - Feed Sync Script
Downloads product feed from Sport X Team and generates split JSON files
for the static GitHub Pages API.

Usage:
    python scripts/sync_feed.py

Feed source: Sport X Team B2B XLSX feed
Output: data/products_ai_enhanced_split/*.json + data/categories.json + data/brands.json + api/stats.json
"""

import json
import math
import os
import sys
from datetime import datetime, timezone
from io import BytesIO
from urllib.request import urlopen, Request

FEED_URL = "https://magb2b.sportxteam.ro/feed/products/08f3fe50dd355cdea695511c156194f6"
PRODUCTS_PER_PART = 250
BIKESTYLISH_BASE_URL = "https://www.bikestylish.ro"

# Paths relative to repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLIT_DIR = os.path.join(REPO_ROOT, "data", "products_ai_enhanced_split")
CATEGORIES_DIR = os.path.join(REPO_ROOT, "data", "categories_ai_enhanced_split")
API_DIR = os.path.join(REPO_ROOT, "api")


def download_feed():
    """Download XLSX feed from Sport X Team."""
    print(f"[1/5] Downloading feed from Sport X Team...")
    req = Request(FEED_URL, headers={"User-Agent": "BikeStylish-Catalog/1.0"})
    with urlopen(req, timeout=120) as response:
        data = response.read()
    print(f"       Downloaded {len(data) / 1024:.1f} KB")
    return BytesIO(data)


def parse_feed(xlsx_data):
    """Parse XLSX feed into product list."""
    try:
        import openpyxl
    except ImportError:
        print("ERROR: openpyxl is required. Install with: pip install openpyxl")
        sys.exit(1)

    print("[2/5] Parsing XLSX feed...")
    wb = openpyxl.load_workbook(xlsx_data, read_only=True, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        print("ERROR: Feed is empty!")
        sys.exit(1)

    headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(rows[0])]
    products = []
    categories_map = {}
    brands_set = set()

    for row in rows[1:]:
        row_dict = dict(zip(headers, row))

        sku = str(row_dict.get("Cod produs - SKU", "")).strip()
        if not sku:
            continue

        name = str(row_dict.get("Nume produs", "")).strip()
        if not name:
            continue

        # Parse price (RRP = recommended retail price for the shop)
        price = _parse_float(row_dict.get("RRP", 0))
        price_net = _parse_float(row_dict.get("RRP (net)", 0))
        wholesale_price = _parse_float(row_dict.get("Pret produs", 0))

        # Parse stock
        stock_raw = str(row_dict.get("Stoc", "0")).strip()
        stock = _parse_int(stock_raw)

        # Determine availability
        if stock > 5:
            availability = "in_stock"
        elif stock > 0:
            availability = "limited"
        else:
            availability = "out_of_stock"

        # Parse category hierarchy
        cat_raw = str(row_dict.get("Categorie principala", "")).strip()
        if cat_raw in ("nan", "None", ""):
            cat_raw = ""
        main_category = _parse_category(cat_raw)

        # Collect secondary categories
        secondary_cats = []
        for i in range(1, 6):
            sec = row_dict.get(f"Categorie secundara {i}")
            if sec and str(sec).strip() and str(sec).strip() != "nan":
                secondary_cats.append(str(sec).strip())

        # Track categories
        if main_category and main_category not in ("None", ""):
            cat_id = _slugify(main_category)
            if not cat_id:
                continue
            if cat_id not in categories_map:
                categories_map[cat_id] = {
                    "id": cat_id,
                    "name": main_category,
                    "full_path": cat_raw,
                    "product_count": 0,
                    "in_stock_count": 0,
                }
            categories_map[cat_id]["product_count"] += 1
            if stock > 0:
                categories_map[cat_id]["in_stock_count"] += 1

        # Parse brand/manufacturer
        brand = str(row_dict.get("Producator", "")).strip()
        if brand and brand not in ("nan", "None", ""):
            brands_set.add(brand)
        else:
            brand = None

        # Parse images
        main_image = str(row_dict.get("URL imagine principala", "")).strip()
        images = []
        if main_image and main_image != "nan":
            images.append(main_image)
        for i in range(1, 5):
            img = row_dict.get(f"URL imagine {i}")
            if img and str(img).strip() and str(img).strip() != "nan":
                img_url = str(img).strip()
                if img_url not in images:
                    images.append(img_url)

        # Parse weight
        weight = _parse_float(row_dict.get("Greutate produs", 0))

        # Parse EAN - clean "None"/"nan" values
        ean_raw = str(row_dict.get("Cod EAN", "")).strip()
        ean = ean_raw if ean_raw not in ("", "nan", "None", "0") else None

        # Build product object
        product = {
            "id": sku,
            "sku": sku,
            "ean": ean,
            "name": name,
            "brand": brand,
            "category": main_category,
            "category_path": cat_raw if cat_raw else None,
            "secondary_categories": secondary_cats if secondary_cats else None,
            "price": price,
            "price_net": price_net,
            "currency": "RON",
            "availability": availability,
            "stock_quantity": stock,
            "weight_kg": weight if weight > 0 else None,
            "url": f"{BIKESTYLISH_BASE_URL}/{_slugify(name)}.html",
            "image": main_image if main_image != "nan" else None,
            "images": images if images else None,
        }

        # Remove None values to keep JSON clean
        product = {k: v for k, v in product.items() if v is not None}

        # Enrich with tags, specs, and context
        product = _enrich_product(product)

        products.append(product)

    wb.close()

    brands = sorted(brands_set)
    categories = sorted(categories_map.values(), key=lambda c: c["name"])

    print(f"       Parsed {len(products)} products, {len(categories)} categories, {len(brands)} brands")
    return products, categories, brands


def write_split_json(products, categories, brands):
    """Write products to split JSON files (matching existing structure)."""
    print("[3/5] Writing split JSON files...")

    now = datetime.now(timezone.utc).isoformat()
    total = len(products)
    total_parts = math.ceil(total / PRODUCTS_PER_PART)

    os.makedirs(SPLIT_DIR, exist_ok=True)

    # Remove old part files
    for f in os.listdir(SPLIT_DIR):
        if f.startswith("products_ai_enhanced_part_") and f.endswith(".json"):
            os.remove(os.path.join(SPLIT_DIR, f))

    # Write product parts
    for part_num in range(1, total_parts + 1):
        start = (part_num - 1) * PRODUCTS_PER_PART
        end = min(start + PRODUCTS_PER_PART, total)
        chunk = products[start:end]

        part_data = {
            "last_updated": now,
            "total_products": len(chunk),
            "source": "sportxteam_feed",
            "part_info": {
                "part_number": part_num,
                "total_parts": total_parts,
                "product_range": f"{start + 1}-{end}",
                "original_total": total,
            },
            "products": chunk,
            "categories": categories,
            "brands": brands,
        }

        filename = f"products_ai_enhanced_part_{part_num:02d}.json"
        filepath = os.path.join(SPLIT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(part_data, f, ensure_ascii=False, indent=2)

    # Update split_info.txt
    with open(os.path.join(SPLIT_DIR, "split_info.txt"), "w", encoding="utf-8") as f:
        f.write(f"Informatii despre impartirea fisierului products_ai_enhanced.json\n")
        f.write(f"Data impartirii: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Numarul de fisiere create: {total_parts}\n")
        f.write(f"Produse per fisier: {PRODUCTS_PER_PART}\n\n")
        for part_num in range(1, total_parts + 1):
            start = (part_num - 1) * PRODUCTS_PER_PART + 1
            end = min(part_num * PRODUCTS_PER_PART, total)
            f.write(f"- products_ai_enhanced_part_{part_num:02d}.json: produse {start}-{end}\n")

    print(f"       Wrote {total_parts} product files")

    # Write categories
    os.makedirs(CATEGORIES_DIR, exist_ok=True)
    for f_name in os.listdir(CATEGORIES_DIR):
        if f_name.endswith(".json"):
            os.remove(os.path.join(CATEGORIES_DIR, f_name))

    cat_data = {
        "last_updated": now,
        "total_categories": len(categories),
        "categories": categories,
    }
    with open(os.path.join(CATEGORIES_DIR, "categories_ai_enhanced_part_01.json"), "w", encoding="utf-8") as f:
        json.dump(cat_data, f, ensure_ascii=False, indent=2)

    # Write brands
    brands_data = {
        "last_updated": now,
        "total_brands": len(brands),
        "brands": brands,
    }
    with open(os.path.join(REPO_ROOT, "data", "brands.json"), "w", encoding="utf-8") as f:
        json.dump(brands_data, f, ensure_ascii=False, indent=2)

    return total_parts


def write_api_index(products, categories, brands, total_parts):
    """Write API index and stats files for AI discovery."""
    print("[4/5] Writing API index and stats...")

    os.makedirs(API_DIR, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    # Calculate stats
    prices = [p["price"] for p in products if p.get("price", 0) > 0]
    in_stock = sum(1 for p in products if p.get("availability") == "in_stock")
    limited = sum(1 for p in products if p.get("availability") == "limited")
    out_of_stock = sum(1 for p in products if p.get("availability") == "out_of_stock")

    # Brand distribution
    brand_counts = {}
    for p in products:
        b = p.get("brand", "Unknown")
        brand_counts[b] = brand_counts.get(b, 0) + 1

    stats = {
        "last_updated": now,
        "catalog": {
            "total_products": len(products),
            "total_categories": len(categories),
            "total_brands": len(brands),
            "total_parts": total_parts,
            "products_per_part": PRODUCTS_PER_PART,
        },
        "availability": {
            "in_stock": in_stock,
            "limited": limited,
            "out_of_stock": out_of_stock,
        },
        "pricing": {
            "currency": "RON",
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
        },
        "top_brands": dict(sorted(brand_counts.items(), key=lambda x: -x[1])[:20]),
        "source": "Sport X Team B2B Feed",
        "website": "https://www.bikestylish.ro",
    }

    with open(os.path.join(API_DIR, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # Write catalog index (lightweight, for AI agents to discover the structure)
    catalog_index = {
        "name": "BikeStylish Product Catalog API",
        "description": "Complete product catalog for bikestylish.ro - Romanian bicycle parts, accessories, and equipment store. Powered by Sport X Team.",
        "website": "https://www.bikestylish.ro",
        "api_base": "https://endimion2k.github.io/bikestylish-catalog",
        "last_updated": now,
        "endpoints": {
            "stats": "/api/stats.json",
            "brands": "/data/brands.json",
            "categories": "/data/categories_ai_enhanced_split/categories_ai_enhanced_part_01.json",
            "products": {
                "pattern": "/data/products_ai_enhanced_split/products_ai_enhanced_part_{NN}.json",
                "parts": total_parts,
                "products_per_part": PRODUCTS_PER_PART,
                "total_products": len(products),
                "example": "/data/products_ai_enhanced_split/products_ai_enhanced_part_01.json",
            },
        },
        "product_schema": {
            "id": "string - SKU code",
            "sku": "string - same as id",
            "ean": "string - EAN barcode",
            "name": "string - product name (Romanian)",
            "brand": "string - manufacturer name",
            "category": "string - main category name",
            "category_path": "string - full category hierarchy (e.g. 'COMPONENTE > Anvelope')",
            "price": "number - recommended retail price in RON",
            "currency": "string - always RON",
            "availability": "string - in_stock | limited | out_of_stock",
            "stock_quantity": "integer - exact stock count",
            "weight_kg": "number - product weight in kg (when available)",
            "url": "string - product page URL on bikestylish.ro",
            "image": "string - main product image URL",
            "images": "array - all product image URLs",
            "tags": "array - searchable tags (brand, category, bike type, wheel size, material)",
            "specs": "object - extracted specifications (wheel_size, bike_type, material, speeds, dimensions, valve_type, color)",
            "category_description": "string - English description of what this product category is (for AI context)",
        },
    }

    with open(os.path.join(API_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(catalog_index, f, ensure_ascii=False, indent=2)

    print(f"       Stats: {len(products)} products, {in_stock} in stock, avg price {stats['pricing']['avg_price']} RON")


def write_sync_report(products, categories, brands, total_parts):
    """Write a sync report for logging."""
    print("[5/5] Writing sync report...")

    now = datetime.now(timezone.utc).isoformat()
    report = {
        "sync_time": now,
        "feed_url": FEED_URL,
        "results": {
            "total_products": len(products),
            "total_categories": len(categories),
            "total_brands": len(brands),
            "total_parts": total_parts,
            "in_stock": sum(1 for p in products if p.get("availability") == "in_stock"),
            "out_of_stock": sum(1 for p in products if p.get("availability") == "out_of_stock"),
        },
        "status": "success",
    }

    with open(os.path.join(REPO_ROOT, "last_sync.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"       Sync complete!")
    return report


# --- Product Enrichment ---

# Wheel sizes found in product names
_WHEEL_SIZES = ["29", "27.5", "27,5", "26", "24", "20", "18", "16", "14", "12", "700C", "700c", "650B", "650b"]

# Bike type keywords (Romanian + English)
_BIKE_TYPES = {
    "MTB": ["mtb", "mountain", "munte"],
    "Road": ["road", "sosea", "cursiera", "drop bar"],
    "BMX": ["bmx"],
    "E-Bike": ["e-bike", "ebike", "electric", "e bike"],
    "Gravel": ["gravel", "cx", "cyclocross"],
    "City/Trekking": ["city", "trekking", "oras", "urban"],
    "Downhill": ["downhill", "dh"],
    "Enduro": ["enduro"],
    "Trail": ["trail", "all-mountain", "all mountain"],
    "Copii": ["copii", "copil", "kids", "junior"],
    "Fixie": ["fixie", "single speed", "fixed gear"],
}

# Material keywords
_MATERIALS = {
    "Aluminiu": ["aluminiu", "aluminum", "alu", "alloy"],
    "CrMo": ["crmo", "cr-mo", "cromoly", "chromoly"],
    "Carbon": ["carbon"],
    "Otel": ["otel", "steel", "hi-ten"],
    "Titan": ["titan", "titanium"],
    "Nylon": ["nylon"],
    "Plastic": ["plastic", "polimer"],
}

# Color keywords
_COLORS = [
    "negru", "alb", "rosu", "albastru", "verde", "galben", "portocaliu",
    "gri", "argintiu", "auriu", "mov", "purple", "roz", "pink",
    "cyan", "orange", "blue", "red", "green", "black", "white",
    "silver", "gold", "grey", "gray", "transparent",
]

# Category descriptions for AI context
_CATEGORY_CONTEXT = {
    "Anvelope pe Sarma": "Wire bead bicycle tires - standard mounting, budget-friendly",
    "Anvelope Pliabile": "Folding bead bicycle tires - lighter weight, easier storage, premium",
    "Camere de bicicleta": "Inner tubes for bicycles - essential spare part",
    "Pedale": "Bicycle pedals - flat/platform or clipless (SPD)",
    "Pedale SPD": "Clipless pedals - click-in system for cycling shoes",
    "Ghidoane": "Handlebars - flat, riser, drop bar styles",
    "Pipe Ghidon": "Stems - connect handlebars to steerer tube",
    "Tije Ghidon": "Steerer extensions / handlebar risers",
    "Lanturi": "Bicycle chains - by speed count (6-12 speed)",
    "Pinioane": "Cassettes and freewheels - rear gear clusters",
    "Angrenaje": "Cranksets - pedal arms and chainrings",
    "Manete Schimbator": "Shift levers / shifters",
    "Schimbator Pinioane": "Rear derailleurs",
    "Schimbator Foi": "Front derailleurs",
    "Frane V-Brake": "V-Brake rim brakes and components",
    "Placute Frana Disc": "Disc brake pads - sintered or organic",
    "Disc frana": "Brake rotors/discs",
    "Etrier frana": "Brake calipers",
    "Accesorii Frane Hidraulice": "Hydraulic brake accessories and service parts",
    "Roti Fata": "Front wheels - complete, ready to mount",
    "Roti Spate": "Rear wheels - complete, ready to mount",
    "Set Roti": "Wheelsets - front + rear wheel pair",
    "Jante": "Rims - for wheel building",
    "Butuci Roata": "Wheel hubs - front and rear",
    "Furci": "Suspension and rigid forks",
    "Cuvete": "Headsets - steerer tube bearings",
    "Monobloc": "Bottom brackets",
    "Tije Șa": "Seatposts",
    "Coliere Șa": "Seat clamps",
    "Șei": "Saddles/seats",
    "Mansoane": "Handlebar grips",
    "Ghidoline": "Bar tape - for drop handlebars",
    "Lumini": "Bicycle lights - front and rear",
    "Antifurturi": "Bike locks - U-locks, cable locks, chain locks",
    "Pompe": "Bicycle pumps - floor and portable",
    "Aparatori noroi": "Fenders/mudguards",
    "Casti": "Helmets",
    "Manusi": "Cycling gloves",
    "Ureche cadru": "Derailleur hangers - frame-specific replacement parts",
    "Suport bidon si bidon": "Bottle cages and water bottles",
    "Borsete si Genti": "Bags and panniers for bicycles",
    "Unelte Speciale": "Specialized bicycle tools",
    "Unelte Universale": "General purpose bicycle tools",
    "Ingrijire si Lubrifiere": "Bike care - lubricants, cleaners, degreasers",
}


def _enrich_product(product):
    """Extract tags, specs, and context from product name and category. Only factual data."""
    import re

    name = product.get("name", "")
    name_lower = name.lower()
    category = product.get("category", "")
    cat_path = product.get("category_path", "")
    brand = product.get("brand", "")

    tags = set()
    specs = {}

    # Extract wheel size - only from tire/wheel-related categories or clear dimension patterns
    wheel_categories = {"anvelope", "camere", "roti", "jante", "cauciuc", "tubeless"}
    is_wheel_related = any(wc in category.lower() or wc in cat_path.lower() for wc in wheel_categories)

    if is_wheel_related:
        for size in _WHEEL_SIZES:
            # Match "29 x", "27.5x", "26x", "700C" patterns (wheel dimensions)
            size_pattern = re.escape(size).replace(r"\.", r"[.,]")
            if re.search(rf'(?<!\d){size_pattern}\s*[xX/"]', name) or \
               re.search(rf'(?<!\d){size_pattern}(?:\s|$|["\'])', name) and size in ("700C", "700c", "650B", "650b"):
                normalized = size.replace(",", ".").upper()
                specs["wheel_size"] = normalized
                tags.add(f"{normalized} inch" if normalized not in ("700C", "650B") else normalized)
                break

    # Extract bike type
    bike_types = []
    search_text = f"{name_lower} {cat_path.lower()}"
    for bike_type, keywords in _BIKE_TYPES.items():
        if any(kw in search_text for kw in keywords):
            bike_types.append(bike_type)
            tags.add(bike_type)
    if bike_types:
        specs["bike_type"] = bike_types

    # Extract material
    for material, keywords in _MATERIALS.items():
        if any(kw in name_lower for kw in keywords):
            specs["material"] = material
            tags.add(material)
            break

    # Extract color
    for color in _COLORS:
        if color in name_lower:
            specs["color"] = color.capitalize()
            break

    # Extract speed count (for chains, cassettes, shifters)
    speed_match = re.search(r'(\d{1,2})\s*(?:speed|viteze|s(?:pd)?)\b', name_lower)
    if not speed_match:
        speed_match = re.search(r'(\d{1,2})v\b', name_lower)
    if speed_match:
        speed = int(speed_match.group(1))
        if 1 <= speed <= 13:
            specs["speeds"] = speed
            tags.add(f"{speed} viteze")

    # Extract dimensions from name (e.g., "29 x 2.40", "26 x 1.75-2.125")
    dim_match = re.search(r'(\d{2,3})\s*x\s*([\d.,]+(?:\s*-\s*[\d.,]+)?)', name)
    if dim_match:
        specs["dimensions"] = f"{dim_match.group(1)} x {dim_match.group(2)}"

    # Extract valve type for inner tubes
    if "camera" in name_lower or "camere" in category.lower():
        if "FV" in name or "presta" in name_lower:
            specs["valve_type"] = "Presta (FV)"
            tags.add("Presta")
        elif "AV" in name or "schrader" in name_lower:
            specs["valve_type"] = "Schrader (AV)"
            tags.add("Schrader")
        elif "DV" in name or "dunlop" in name_lower:
            specs["valve_type"] = "Dunlop (DV)"

    # Extract thread size for pedals
    if "pedal" in name_lower:
        if "9/16" in name:
            specs["thread"] = '9/16"'
        elif "1/2" in name:
            specs["thread"] = '1/2"'

    # Add brand as tag
    if brand and brand not in ("Unknown", "None", ""):
        tags.add(brand)

    # Add category as tag
    if category:
        tags.add(category)

    # Add category context (what this type of product IS)
    if category in _CATEGORY_CONTEXT:
        product["category_description"] = _CATEGORY_CONTEXT[category]

    # Add main category from path
    if cat_path:
        parts = [p.strip() for p in cat_path.split(">")]
        if len(parts) > 1:
            tags.add(parts[0])  # e.g., "COMPONENTE", "ACCESORII"

    # Set enriched data
    if tags:
        product["tags"] = sorted(tags)
    if specs:
        product["specs"] = specs

    return product


# --- Helpers ---

def _parse_float(val):
    try:
        return round(float(val), 2)
    except (ValueError, TypeError):
        return 0.0


def _parse_int(val):
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def _parse_category(cat_path):
    """Extract the most specific category from 'COMPONENTE > Anvelope - Camere > Anvelope pe Sarma'."""
    if not cat_path or cat_path in ("nan", "None", ""):
        return None
    parts = [p.strip() for p in cat_path.split(">")]
    result = parts[-1] if parts else None
    return result if result else None


def _slugify(text):
    """Create a URL-friendly slug from text."""
    import re
    text = text.lower().strip()
    # Romanian character replacements
    replacements = {
        "ă": "a", "â": "a", "î": "i", "ș": "s", "ş": "s",
        "ț": "t", "ţ": "t", "Ă": "A", "Â": "A", "Î": "I",
        "Ș": "S", "Ş": "S", "Ț": "T", "Ţ": "T",
    }
    for ro, en in replacements.items():
        text = text.replace(ro, en)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def main():
    print("=" * 60)
    print("BikeStylish Catalog - Feed Sync")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    xlsx_data = download_feed()
    products, categories, brands = parse_feed(xlsx_data)

    if not products:
        print("ERROR: No products parsed from feed! Aborting.")
        sys.exit(1)

    total_parts = write_split_json(products, categories, brands)
    write_api_index(products, categories, brands, total_parts)
    report = write_sync_report(products, categories, brands, total_parts)

    print()
    print("=" * 60)
    print(f"DONE: {report['results']['total_products']} products synced")
    print(f"      {report['results']['in_stock']} in stock / {report['results']['out_of_stock']} out of stock")
    print(f"      {report['results']['total_parts']} JSON parts written")
    print("=" * 60)


if __name__ == "__main__":
    main()
