#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyzer comprehensiv SEO și GEO pentru documentele JSON BikeStylish
Analizează și optimizează datele pentru performanță SEO și targeting geografic
"""

import json
import re
from datetime import datetime
from collections import defaultdict, Counter
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SEOGeoAnalyzer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.geo_cities = {
            "bucuresti": {"priority": 1.0, "population": 1883425, "region": "Bucuresti-Ilfov"},
            "cluj-napoca": {"priority": 0.9, "population": 324576, "region": "Transilvania"},
            "timisoara": {"priority": 0.9, "population": 319279, "region": "Banat"},
            "iasi": {"priority": 0.9, "population": 290422, "region": "Moldova"},
            "constanta": {"priority": 0.8, "population": 283872, "region": "Dobrogea"},
            "craiova": {"priority": 0.8, "population": 269506, "region": "Oltenia"},
            "brasov": {"priority": 0.8, "population": 253200, "region": "Transilvania"},
            "galati": {"priority": 0.7, "population": 249432, "region": "Moldova"},
            "ploiesti": {"priority": 0.7, "population": 201226, "region": "Muntenia"},
            "oradea": {"priority": 0.7, "population": 196367, "region": "Crisana"},
            "braila": {"priority": 0.6, "population": 180302, "region": "Moldova"},
            "arad": {"priority": 0.6, "population": 159704, "region": "Crisana"},
            "pitesti": {"priority": 0.6, "population": 155383, "region": "Muntenia"},
            "sibiu": {"priority": 0.6, "population": 147245, "region": "Transilvania"},
            "bacau": {"priority": 0.6, "population": 144307, "region": "Moldova"},
            "targu-mures": {"priority": 0.5, "population": 134290, "region": "Transilvania"},
            "baia-mare": {"priority": 0.5, "population": 123738, "region": "Maramures"},
            "buzau": {"priority": 0.5, "population": 115494, "region": "Muntenia"},
            "satu-mare": {"priority": 0.5, "population": 102441, "region": "Maramures"},
            "botosani": {"priority": 0.5, "population": 106847, "region": "Moldova"}
        }
        
        self.cycling_keywords = {
            "high_intent": [
                "bicicleta", "biciclete", "bike", "mtb", "road bike", "ciclism", "pedalare",
                "anvelope bicicleta", "ghidon", "sa bicicleta", "pedale", "lant bicicleta",
                "frane bicicleta", "schimbator", "casca bicicleta", "lanterna bicicleta"
            ],
            "medium_intent": [
                "accesorii bicicleta", "piese bicicleta", "service bicicleta", "reparatii bicicleta",
                "transport bicicleta", "depozitare bicicleta", "intretinere bicicleta"
            ],
            "geo_modifiers": [
                "magazin", "shop", "service", "reparatii", "vanzare", "cumpar",
                "second hand", "nou", "oferta", "promotie", "reducere"
            ],
            "seasonal": [
                "vara", "iarna", "primavara", "toamna", "sezon", "outdoor",
                "ture", "excursii", "vacanta", "weekend"
            ]
        }
        
    def analyze_all_data(self):
        """Analizează toate documentele JSON pentru SEO și GEO"""
        logger.info("🔍 Începem analiza SEO și GEO pentru toate documentele JSON...")
        
        analysis_result = {
            "analysis_timestamp": datetime.now().isoformat(),
            "files_analyzed": [],
            "seo_opportunities": {},
            "geo_opportunities": {},
            "content_gaps": {},
            "technical_seo": {},
            "keyword_analysis": {},
            "recommendations": []
        }
        
        # Analizează fiecare fișier JSON
        json_files = [
            "categories_ai_enhanced.json",
            "products_ai_enhanced.json", 
            "brands.json",
            "categories.json",
            "products.json"
        ]
        
        for file in json_files:
            try:
                logger.info(f"📊 Analizez fișierul: {file}")
                file_analysis = self._analyze_json_file(file)
                analysis_result["files_analyzed"].append(file)
                analysis_result["seo_opportunities"][file] = file_analysis["seo"]
                analysis_result["geo_opportunities"][file] = file_analysis["geo"]
                analysis_result["content_gaps"][file] = file_analysis["gaps"]
                analysis_result["technical_seo"][file] = file_analysis["technical"]
                
            except Exception as e:
                logger.error(f"❌ Eroare la analiza {file}: {e}")
        
        # Analiză globală keyword-uri
        analysis_result["keyword_analysis"] = self._global_keyword_analysis()
        
        # Generează recomandări
        analysis_result["recommendations"] = self._generate_recommendations(analysis_result)
        
        # Salvează rezultatele
        self._save_analysis(analysis_result)
        
        return analysis_result
    
    def _analyze_json_file(self, filename):
        """Analizează un fișier JSON specific"""
        file_path = f"{self.data_dir}/{filename}"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        analysis = {
            "seo": self._analyze_seo_data(data, filename),
            "geo": self._analyze_geo_opportunities(data, filename),
            "gaps": self._identify_content_gaps(data, filename),
            "technical": self._analyze_technical_seo(data, filename)
        }
        
        return analysis
    
    def _analyze_seo_data(self, data, filename):
        """Analizează datele pentru oportunități SEO"""
        seo_analysis = {
            "meta_analysis": {},
            "content_analysis": {},
            "url_analysis": {},
            "schema_analysis": {},
            "keyword_density": {},
            "title_optimization": {},
            "description_optimization": {}
        }
        
        if filename == "categories_ai_enhanced.json":
            categories = data.get("categories", [])
            
            # Analiză meta tags
            missing_meta = []
            poor_titles = []
            poor_descriptions = []
            
            for cat in categories:
                cat_id = cat.get("id", "unknown")
                
                # Verifică meta description
                content_struct = cat.get("content_structure", {})
                faq_content = content_struct.get("dropdown_faq_content", {})
                meta_desc = faq_content.get("meta_description")
                
                if not meta_desc:
                    missing_meta.append(cat_id)
                elif len(meta_desc) < 120 or len(meta_desc) > 160:
                    poor_descriptions.append({
                        "id": cat_id,
                        "length": len(meta_desc),
                        "description": meta_desc[:100] + "..."
                    })
                
                # Verifică titluri
                page_title = faq_content.get("page_title")
                if not page_title:
                    poor_titles.append({"id": cat_id, "issue": "missing_title"})
                elif len(page_title) > 60:
                    poor_titles.append({
                        "id": cat_id, 
                        "issue": "too_long", 
                        "length": len(page_title),
                        "title": page_title[:60] + "..."
                    })
            
            seo_analysis["meta_analysis"] = {
                "missing_meta_descriptions": len(missing_meta),
                "poor_descriptions": poor_descriptions[:10],
                "poor_titles": poor_titles[:10],
                "categories_analyzed": len(categories)
            }
            
            # Analiză URL-uri
            url_issues = []
            for cat in categories:
                url = cat.get("url", "")
                cat_id = cat.get("id", "")
                
                # Verifică lungimea URL
                if len(url) > 100:
                    url_issues.append({"id": cat_id, "issue": "too_long", "url": url})
                
                # Verifică duplicate keywords în URL
                url_parts = url.split("/")[-1].split("-")
                if len(url_parts) != len(set(url_parts)):
                    url_issues.append({"id": cat_id, "issue": "duplicate_keywords", "url": url})
            
            seo_analysis["url_analysis"] = {
                "url_issues": url_issues[:10],
                "total_issues": len(url_issues)
            }
            
            # Analiză schema.org
            schema_stats = {"total_schemas": 0, "schema_types": Counter()}
            for cat in categories:
                content_struct = cat.get("content_structure", {})
                faq_content = content_struct.get("dropdown_faq_content", {})
                schemas = faq_content.get("jsonld_schemas", [])
                
                schema_stats["total_schemas"] += len(schemas)
                for schema in schemas:
                    if isinstance(schema, dict):
                        schema_type = schema.get("@type", "Unknown")
                        if isinstance(schema_type, list):
                            for st in schema_type:
                                schema_stats["schema_types"][st] += 1
                        else:
                            schema_stats["schema_types"][schema_type] += 1
            
            seo_analysis["schema_analysis"] = {
                "total_schemas": schema_stats["total_schemas"],
                "most_common_types": dict(schema_stats["schema_types"].most_common(10))
            }
        
        elif filename == "products_ai_enhanced.json":
            # Analiză produse pentru SEO
            products = data.get("products", [])
            
            title_analysis = []
            description_analysis = []
            
            for i, product in enumerate(products[:100]):  # Analizez primele 100
                title = product.get("title", "")
                desc = product.get("description", "")
                
                if len(title) < 30 or len(title) > 60:
                    title_analysis.append({
                        "index": i,
                        "title": title[:50] + "...",
                        "length": len(title),
                        "issue": "length"
                    })
                
                if len(desc) < 120:
                    description_analysis.append({
                        "index": i,
                        "description": desc[:50] + "...",
                        "length": len(desc),
                        "issue": "too_short"
                    })
            
            seo_analysis["title_optimization"] = {
                "products_analyzed": min(len(products), 100),
                "title_issues": title_analysis[:10]
            }
            
            seo_analysis["description_optimization"] = {
                "description_issues": description_analysis[:10]
            }
        
        return seo_analysis
    
    def _analyze_geo_opportunities(self, data, filename):
        """Analizează oportunități de targeting geografic"""
        geo_analysis = {
            "missing_geo_content": [],
            "geo_keyword_opportunities": [],
            "local_seo_gaps": [],
            "city_targeting_potential": {}
        }
        
        if filename == "categories_ai_enhanced.json":
            categories = data.get("categories", [])
            
            for city, city_data in self.geo_cities.items():
                city_opportunities = []
                
                for cat in categories:
                    cat_name = cat.get("name", "").lower()
                    cat_id = cat.get("id", "")
                    
                    # Verifică dacă categoria ar beneficia de geo-targeting
                    if any(keyword in cat_name for keyword in ["service", "magazin", "reparatii"]):
                        city_opportunities.append({
                            "category_id": cat_id,
                            "category_name": cat.get("name", ""),
                            "geo_potential": "high",
                            "suggested_content": f"{cat.get('name', '')} {city.replace('-', ' ').title()}"
                        })
                    elif any(keyword in cat_name for keyword in ["bicicleta", "accesorii", "piese"]):
                        city_opportunities.append({
                            "category_id": cat_id,
                            "category_name": cat.get("name", ""),
                            "geo_potential": "medium",
                            "suggested_content": f"{cat.get('name', '')} - Livrare {city.replace('-', ' ').title()}"
                        })
                
                if city_opportunities:
                    geo_analysis["city_targeting_potential"][city] = {
                        "priority": city_data["priority"],
                        "population": city_data["population"],
                        "opportunities": city_opportunities[:5]  # Top 5 oportunități
                    }
        
        # Identifică lipsurile de conținut geo
        high_value_cities = [city for city, data in self.geo_cities.items() if data["priority"] >= 0.8]
        
        for city in high_value_cities:
            geo_analysis["missing_geo_content"].append({
                "city": city,
                "suggested_pages": [
                    f"Biciclete {city.replace('-', ' ').title()}",
                    f"Service biciclete {city.replace('-', ' ').title()}",
                    f"Magazin biciclete {city.replace('-', ' ').title()}",
                    f"Accesorii biciclete {city.replace('-', ' ').title()}"
                ]
            })
        
        return geo_analysis
    
    def _identify_content_gaps(self, data, filename):
        """Identifică gap-uri în conținut"""
        content_gaps = {
            "missing_faq_content": [],
            "poor_content_categories": [],
            "missing_seasonal_content": [],
            "untapped_keywords": []
        }
        
        if filename == "categories_ai_enhanced.json":
            categories = data.get("categories", [])
            
            for cat in categories:
                cat_id = cat.get("id", "")
                cat_name = cat.get("name", "")
                
                # Verifică FAQ content
                content_struct = cat.get("content_structure", {})
                faq_content = content_struct.get("dropdown_faq_content", {})
                
                if not faq_content:
                    content_gaps["missing_faq_content"].append({
                        "category_id": cat_id,
                        "category_name": cat_name,
                        "priority": "high" if any(kw in cat_name.lower() for kw in self.cycling_keywords["high_intent"]) else "medium"
                    })
                else:
                    combined_faqs = faq_content.get("combined_faqs", [])
                    if len(combined_faqs) < 5:
                        content_gaps["poor_content_categories"].append({
                            "category_id": cat_id,
                            "category_name": cat_name,
                            "faq_count": len(combined_faqs),
                            "recommendation": "Add more FAQ content"
                        })
        
        # Identifică conținut sezonier lipsă
        content_gaps["missing_seasonal_content"] = [
            {"season": "vara", "content": "Ghid ciclism vara - echipament și siguranță"},
            {"season": "iarna", "content": "Biciclete și accesorii pentru ciclism de iarnă"},
            {"season": "primavara", "content": "Pregătirea bicicletei pentru sezonul nou"},
            {"season": "toamna", "content": "Întreținerea bicicletei în sezonul rece"}
        ]
        
        return content_gaps
    
    def _analyze_technical_seo(self, data, filename):
        """Analizează aspecte tehnice SEO"""
        technical_analysis = {
            "json_structure": {},
            "data_quality": {},
            "performance_indicators": {},
            "structured_data": {}
        }
        
        # Analiză structură JSON
        def analyze_json_structure(obj, path="root"):
            if isinstance(obj, dict):
                return {
                    "type": "object",
                    "keys": len(obj.keys()),
                    "nested_objects": sum(1 for v in obj.values() if isinstance(v, dict)),
                    "arrays": sum(1 for v in obj.values() if isinstance(v, list))
                }
            elif isinstance(obj, list):
                return {
                    "type": "array",
                    "length": len(obj),
                    "item_types": list(set(type(item).__name__ for item in obj[:10]))
                }
            else:
                return {"type": type(obj).__name__}
        
        technical_analysis["json_structure"] = analyze_json_structure(data)
        
        # Analiză calitate date
        if filename == "categories_ai_enhanced.json":
            categories = data.get("categories", [])
            
            quality_metrics = {
                "total_categories": len(categories),
                "categories_with_urls": sum(1 for cat in categories if cat.get("url")),
                "categories_with_content": sum(1 for cat in categories if "content_structure" in cat),
                "categories_with_metadata": sum(1 for cat in categories if "content_metadata" in cat),
                "categories_with_ai_content": sum(1 for cat in categories if "ai_enhanced_content" in cat)
            }
            
            technical_analysis["data_quality"] = quality_metrics
            
            # Analiză structured data
            schema_completeness = []
            for cat in categories:
                content_struct = cat.get("content_structure", {})
                faq_content = content_struct.get("dropdown_faq_content", {})
                schemas = faq_content.get("jsonld_schemas", [])
                
                if schemas:
                    for schema in schemas:
                        if isinstance(schema, dict):
                            required_fields = ["@type", "@context"]
                            completeness = sum(1 for field in required_fields if field in schema)
                            schema_completeness.append(completeness / len(required_fields))
            
            avg_completeness = sum(schema_completeness) / len(schema_completeness) if schema_completeness else 0
            technical_analysis["structured_data"] = {
                "schemas_analyzed": len(schema_completeness),
                "average_completeness": round(avg_completeness * 100, 2)
            }
        
        return technical_analysis
    
    def _global_keyword_analysis(self):
        """Analiză globală a keyword-urilor"""
        keyword_analysis = {
            "high_opportunity_keywords": [],
            "competitive_analysis": {},
            "long_tail_opportunities": [],
            "semantic_clusters": {}
        }
        
        # Keywords cu potențial mare pentru ciclism România
        high_opportunity = [
            {"keyword": "bicicleta electrica", "volume": "high", "difficulty": "medium", "intent": "commercial"},
            {"keyword": "piese bicicleta", "volume": "medium", "difficulty": "low", "intent": "commercial"},
            {"keyword": "service bicicleta", "volume": "medium", "difficulty": "low", "intent": "local"},
            {"keyword": "accesorii mtb", "volume": "medium", "difficulty": "medium", "intent": "commercial"},
            {"keyword": "anvelope bicicleta", "volume": "medium", "difficulty": "low", "intent": "commercial"},
            {"keyword": "casca bicicleta", "volume": "medium", "difficulty": "medium", "intent": "commercial"},
            {"keyword": "bicicleta copii", "volume": "high", "difficulty": "medium", "intent": "commercial"},
            {"keyword": "bicicleta de oras", "volume": "medium", "difficulty": "medium", "intent": "commercial"}
        ]
        
        keyword_analysis["high_opportunity_keywords"] = high_opportunity
        
        # Long tail opportunities cu geo targeting
        long_tail = []
        for city, city_data in self.geo_cities.items():
            if city_data["priority"] >= 0.7:
                city_name = city.replace("-", " ").title()
                long_tail.extend([
                    f"bicicleta {city_name}",
                    f"magazin biciclete {city_name}",
                    f"service bicicleta {city_name}",
                    f"piese bicicleta {city_name}",
                    f"accesorii bicicleta {city_name}"
                ])
        
        keyword_analysis["long_tail_opportunities"] = long_tail[:20]
        
        # Clustere semantice
        semantic_clusters = {
            "biciclete_tip": ["mtb", "road bike", "bicicleta electrica", "bicicleta oras", "bicicleta copii"],
            "piese_componente": ["schimbator", "frane", "roti", "anvelope", "lant", "pedale", "sa"],
            "accesorii": ["casca", "lumini", "pompa", "antifurt", "bidon", "geanta"],
            "service_intretinere": ["reparatii", "service", "intretinere", "reglaje", "schimb piese"]
        }
        
        keyword_analysis["semantic_clusters"] = semantic_clusters
        
        return keyword_analysis
    
    def _generate_recommendations(self, analysis_result):
        """Generează recomandări bazate pe analiză"""
        recommendations = []
        
        # Recomandări SEO
        recommendations.extend([
            {
                "type": "seo",
                "priority": "high",
                "title": "Optimizare Meta Descriptions",
                "description": "Adaugă meta descriptions pentru categoriile care nu le au și optimizează lungimea (120-160 caractere)",
                "impact": "Îmbunătățește CTR din SERP și experiența utilizatorului",
                "effort": "medium"
            },
            {
                "type": "seo", 
                "priority": "high",
                "title": "Îmbunătățire Schema.org",
                "description": "Completează schema-urile JSON-LD cu toate câmpurile obligatorii și adaugă FAQ Schema pentru categoriile relevante",
                "impact": "Rich snippets în Google, vizibilitate crescută",
                "effort": "medium"
            },
            {
                "type": "seo",
                "priority": "medium",
                "title": "Optimizare Titluri Pagini",
                "description": "Optimizează titlurile paginilor să fie între 30-60 caractere și să includă keywords principale",
                "impact": "Îmbunătățește ranking-ul și CTR",
                "effort": "low"
            }
        ])
        
        # Recomandări GEO
        recommendations.extend([
            {
                "type": "geo",
                "priority": "high", 
                "title": "Landing Pages Geo-targetate",
                "description": "Creează pagini specifice pentru orașe mari (București, Cluj, Timișoara, Iași)",
                "impact": "Captează trafic local, îmbunătățește conversiile locale",
                "effort": "high"
            },
            {
                "type": "geo",
                "priority": "medium",
                "title": "Local SEO Schema",
                "description": "Adaugă LocalBusiness schema pentru magazinele fizice și service-uri",
                "impact": "Apariție în Google My Business și hărți",
                "effort": "medium"
            },
            {
                "type": "geo",
                "priority": "medium",
                "title": "Conținut Geo în FAQ-uri",
                "description": "Includă întrebări despre livrare, service și disponibilitate în orașe majore",
                "impact": "Răspunde la intent-ul local al utilizatorilor",
                "effort": "low"
            }
        ])
        
        # Recomandări Content
        recommendations.extend([
            {
                "type": "content",
                "priority": "high",
                "title": "Conținut Sezonier",
                "description": "Dezvoltă conținut pentru fiecare sezon (ghiduri, sfaturi, produse recomandate)",
                "impact": "Captează trafic sezonier și îmbunătățește engagement-ul",
                "effort": "medium"
            },
            {
                "type": "content",
                "priority": "medium",
                "title": "FAQ-uri Extinse",
                "description": "Adaugă mai multe FAQ-uri pentru categoriile cu conținut limitat",
                "impact": "Îmbunătățește experiența utilizatorului și timpul petrecut pe site",
                "effort": "medium"
            }
        ])
        
        # Recomandări Tehnice
        recommendations.extend([
            {
                "type": "technical",
                "priority": "medium",
                "title": "Optimizare Performanță JSON",
                "description": "Comprimă și optimizează structura JSON pentru încărcare mai rapidă",
                "impact": "Îmbunătățește viteza site-ului și experiența utilizatorului",
                "effort": "low"
            },
            {
                "type": "technical",
                "priority": "low",
                "title": "Validare Structured Data",
                "description": "Implementează validare automată pentru schema.org data",
                "impact": "Asigură corectitudinea datelor structurate",
                "effort": "medium"
            }
        ])
        
        return recommendations
    
    def _save_analysis(self, analysis_result):
        """Salvează rezultatele analizei"""
        filename = f"seo_geo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Analiza SEO și GEO salvată în: {filename}")
        
        # Creează și un raport sumar
        self._create_summary_report(analysis_result)
    
    def _create_summary_report(self, analysis_result):
        """Creează un raport sumar lizibil"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"seo_geo_summary_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 🔍 Raport Analiză SEO și GEO - BikeStylish\n\n")
            f.write(f"**Data analizei:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
            
            # Sumar executiv
            f.write("## 📊 Sumar Executiv\n\n")
            files_count = len(analysis_result["files_analyzed"])
            f.write(f"- **Fișiere analizate:** {files_count}\n")
            f.write(f"- **Recomandări generate:** {len(analysis_result['recommendations'])}\n\n")
            
            # Recomandări prioritare
            f.write("## 🎯 Recomandări Prioritare\n\n")
            high_priority_recs = [r for r in analysis_result["recommendations"] if r["priority"] == "high"]
            
            for i, rec in enumerate(high_priority_recs, 1):
                f.write(f"### {i}. {rec['title']} ({rec['type'].upper()})\n")
                f.write(f"**Descriere:** {rec['description']}\n\n")
                f.write(f"**Impact:** {rec['impact']}\n\n")
                f.write(f"**Efort:** {rec['effort']}\n\n")
                f.write("---\n\n")
            
            # Oportunități GEO
            f.write("## 🗺️ Oportunități Geografice\n\n")
            geo_cats = analysis_result.get("geo_opportunities", {}).get("categories_ai_enhanced.json", {})
            city_potential = geo_cats.get("city_targeting_potential", {})
            
            f.write("### Orașe cu Potențial Mare:\n\n")
            for city, data in sorted(city_potential.items(), key=lambda x: x[1]["priority"], reverse=True)[:5]:
                f.write(f"- **{city.replace('-', ' ').title()}** (Prioritate: {data['priority']}, Pop: {data['population']:,})\n")
                f.write(f"  - Oportunități: {len(data['opportunities'])}\n")
            
            f.write("\n")
            
            # Keywords de înaltă valoare
            keyword_analysis = analysis_result.get("keyword_analysis", {})
            high_opp_keywords = keyword_analysis.get("high_opportunity_keywords", [])
            
            f.write("## 🔑 Keywords Prioritare\n\n")
            for kw in high_opp_keywords[:10]:
                f.write(f"- **{kw['keyword']}** - Volume: {kw['volume']}, Dificultate: {kw['difficulty']}, Intent: {kw['intent']}\n")
            
            f.write("\n")
            
            # Acțiuni următoare
            f.write("## 📋 Acțiuni Următoare\n\n")
            f.write("1. **Implementare Meta Descriptions** - Prioritate înaltă, efort mediu\n")
            f.write("2. **Creare Landing Pages Geo** - Prioritate înaltă, efort mare\n") 
            f.write("3. **Optimizare Schema.org** - Prioritate înaltă, efort mediu\n")
            f.write("4. **Dezvoltare Conținut Sezonier** - Prioritate înaltă, efort mediu\n")
            f.write("5. **Extindere FAQ-uri** - Prioritate medie, efort mediu\n\n")
            
            f.write("---\n")
            f.write("*Analiză generată automat de SEOGeoAnalyzer*\n")
        
        logger.info(f"📝 Raport sumar salvat în: {filename}")

def main():
    """Funcția principală"""
    print("🔍 ANALYZER SEO ȘI GEO pentru BikeStylish")
    print("=" * 60)
    
    analyzer = SEOGeoAnalyzer()
    
    print("📊 Începem analiza comprehensivă...")
    analysis_result = analyzer.analyze_all_data()
    
    print(f"\n✅ Analiză completă!")
    print(f"📁 Fișiere analizate: {len(analysis_result['files_analyzed'])}")
    print(f"🎯 Recomandări generate: {len(analysis_result['recommendations'])}")
    print(f"🗺️ Orașe analizate pentru GEO: {len(analyzer.geo_cities)}")
    
    # Afișează un preview al recomandărilor
    print(f"\n🏆 TOP 3 RECOMANDĂRI PRIORITARE:")
    high_priority = [r for r in analysis_result["recommendations"] if r["priority"] == "high"][:3]
    for i, rec in enumerate(high_priority, 1):
        print(f"   {i}. {rec['title']} ({rec['type'].upper()})")
        print(f"      {rec['description'][:80]}...")
    
    print(f"\n📊 Pentru detalii complete, consultă fișierele generate.")

if __name__ == "__main__":
    main()
