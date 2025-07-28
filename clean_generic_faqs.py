#!/usr/bin/env python3
"""
Script pentru eliminarea întrebărilor generice repetitive din FAQ-uri
și înlocuirea lor cu conținut specific pentru fiecare categorie.
"""

import json
import re

def load_categories():
    """Încarcă categoriile din JSON"""
    try:
        with open('data/categories_ai_enhanced.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Eroare la încărcarea JSON: {e}")
        return None

def save_categories(data):
    """Salvează categoriile în JSON"""
    try:
        with open('data/categories_ai_enhanced.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Eroare la salvarea JSON: {e}")
        return False

def is_generic_question(question):
    """Verifică dacă o întrebare este generică"""
    generic_patterns = [
        r"Cum aleg .* potrivite pentru nevoile mele\?",
        r"Care sunt prețurile pentru .* și cum aleg categoria de preț potrivită\?",
        r"Ce mărci de .* recomandați și care sunt diferențele\?",
        r"Ce specificații tehnice sunt importante pentru .*\?",
        r"Cum utilizez și întretin corect .*\?",
        r"Cum se montează .* și ce scule îmi trebuie\?"
    ]
    
    for pattern in generic_patterns:
        if re.search(pattern, question):
            return True
    return False

def generate_specific_faqs(category_id, category_name, real_data=None):
    """Generează FAQ-uri specifice pentru o categorie"""
    
    # FAQ-uri specifice bazate pe categoria și datele reale
    specific_faqs = []
    
    if category_id in ['accesorii-bicicleta', 'accesorii']:
        specific_faqs = [
            {
                "question": "Care sunt accesoriile esențiale pentru siguranța în trafic?",
                "answer": "🚨 SIGURANȚĂ MAXIMĂ: Lumini LED (față minimum 400 lumeni, spate cu mod flash), reflectorizante pe roți și cadru, antifurt nivel 8+, sonerie puternică, aparătoare noroi pentru vizibilitate. Pentru ciclism nocturn: vestă reflectorizantă, casca cu LED integrat, lumini suplimentare pe brațe/picioare."
            },
            {
                "question": "Cum îmi aleg coșul sau geanta potrivită pentru transportul zilnic?",
                "answer": "📦 PENTRU TRANSPORT ZILNIC: Coș față (5-15kg) pentru cumpărături ușoare, geantă ghidon waterproof pentru documente/telefon, coș spate (20-25kg) pentru bagaje mari. Material: aluminiu pentru durabilitate, detașabil pentru siguranță, cu sistem de fixare rapid-release."
            },
            {
                "question": "Ce accesorii îmi îmbunătățesc confortul pe distanțe lungi?",
                "answer": "💺 CONFORT MAXIM: Mansoane ergonomice cu gel, șa cu suspensie și canelură centrală, aparătoare noroi pentru protecție, suport bidon pentru hidratare constantă, geantă șa pentru unelte repair kit, mansoane cu bar-ends pentru poziții multiple ale mâinilor."
            }
        ]
    
    elif category_id in ['remorci-transport-copii', 'roti-ajutatoare', 'scaune-pentru-copii', 'articole-copii-roti-ajutatoare']:
        specific_faqs = [
            {
                "question": "De la ce vârstă poate folosi copilul acest produs?",
                "answer": "👶 SIGURANȚĂ COPII: Scaune față: 9 luni - 15kg (2-3 ani), Scaune spate: 9 luni - 22kg (6 ani), Remorci: 6 luni - 45kg (2 copii), Rotițe ajutătoare: 3-8 ani (12-20 inch). Întotdeauna cu cască omologată și harnașament în 5 puncte."
            },
            {
                "question": "Cum mă asigur că produsul este montat corect și sigur?",
                "answer": "🔧 MONTAJ SIGUR: Verifică compatibilitatea cu diametrul cadrului, respectă greutatea maximă, testează stabilitatea înainte de prima ieșire, verifică strângerea șuruburilor la fiecare 100km. Montaj profesional recomandat pentru siguranță maximă."
            },
            {
                "question": "Ce echipament de protecție este obligatoriu pentru copii?",
                "answer": "🛡️ PROTECȚIE COMPLETĂ: Cască omologată (EN1078), obligatorie sub 14 ani, harnașament în 5 puncte pentru scaune, învelitori de protecție pentru vremea rea, benzi reflectorizante pentru vizibilitate, încălțăminte sigură (nu sandale)."
            }
        ]
    
    elif category_id in ['cricuri-de-mijloc', 'cricuri-e-bike']:
        specific_faqs = [
            {
                "question": "Care este diferența între cricurile laterale și cele de centru?",
                "answer": "⚖️ TIPURI CRICURI: Lateral (standard): pentru parcare temporară, ușor de folosit, mai puțin stabil. Centru: stabilitate maximă, nu afectează echilibrul, ideal pentru încărcare/descărcare, recomandat pentru e-bike și cargo bike. Material aluminiu pentru greutate redusă."
            },
            {
                "question": "Cum aleg cricul potrivit pentru greutatea bicicletei mele?",
                "answer": "⚡ E-BIKE & GREUTATE: Biciclete standard (15-20kg): cric standard. E-bike (25-30kg): cric ranforsat pentru e-bike cu bază lărgită. Cargo/transport (40kg+): cric dublu sau industrial. Verifică capacitatea maximă și punctul de fixare pe cadru."
            },
            {
                "question": "De ce nu se ridică cricul complet sau se blochează?",
                "answer": "🔧 PROBLEME COMUNE: Curățare regulată de noroi/nisip, lubrifiere articulații cu spray silicon, ajustare tensiune arc, verificare uzură plăcuță contact. Pentru cricuri cu resort: înlocuire la 2-3 ani utilizare intensivă. Evită forțarea mecanismului."
            }
        ]
    
    elif category_id in ['lumini', 'lumini-fata', 'lumini-spate', 'seturi-lumini']:
        specific_faqs = [
            {
                "question": "Câți lumeni am nevoie pentru diferite tipuri de ciclism?",
                "answer": "💡 PUTERE OPTIMĂ: Urban/oraș: 200-400 lumeni (vizibilitate). Șosea/drum: 400-800 lumeni (iluminare). Mountain/trail: 800-1600+ lumeni (vedere clară). Spate: 50-100 lumeni constant, 200+ lumeni flash. USB-C fast charge, autonomie min 4h pentru distanțe lungi."
            },
            {
                "question": "Cum îmi aleg setul de lumini pentru respectarea legii?",
                "answer": "⚖️ LEGISLAȚIE ROMÂNIA: Obligatoriu între apus și răsărit + vizibilitate redusă. Față: lumină albă constantă, Spate: lumină roșie constantă sau intermitentă. Reflectorizante: albe față, roșii spate, galbene lateral. Verifică omologarea StVZO pentru Germania/UE."
            },
            {
                "question": "Care sunt avantajele luminilor cu senzori automat?",
                "answer": "🤖 TEHNOLOGIE SMART: Pornire automată la întuneric, ajustare intensitate după lumina ambientală, economie baterie cu oprire automată, conectivitate Bluetooth pentru control smartphone. Ideal pentru commuting zilnic și uitat să aprinzi/stingi manual."
            }
        ]
        
    elif category_id in ['cosuri-pentru-biciclete']:
        specific_faqs = [
            {
                "question": "Care este diferența între coșurile de față și cele de spate?",
                "answer": "📦 POZIȚIONARE OPTIMĂ: Față (ghidon): 5-15kg, acces rapid, afectează direcția. Spate (portbagaj): 20-25kg, stabilitate mai bună, nu afectează manevrarea. Pentru cumpărături: spate, pentru acces rapid (geantă, telefon): față."
            },
            {
                "question": "Cum aleg materialul potrivit pentru coș?",
                "answer": "🧺 MATERIALE: Plastic dur: ușor, impermeabil, colorat, ieftin. Aluminiu: durabil, elegant, rezistent la impact. Lemn/ratan: estetic vintage, necesită întreținere. Metalic: foarte durabil, mai greu. Pentru uz zilnic: plastic sau aluminiu."
            },
            {
                "question": "Pot monta coș pe orice tip de bicicletă?",
                "answer": "🔧 COMPATIBILITATE: Verifică tipul ghidonului (22.2mm standard), existența portbagajului pentru coș spate, greutatea maximă suportată. MTB: adaptoare speciale necesare. E-bike: verifică interferența cu bateria. Road bike: coșuri minimaliste recomandate."
            }
        ]
    
    else:
        # FAQ-uri generale pentru alte categorii
        specific_faqs = [
            {
                "question": f"Care sunt principalele caracteristici de căutat la {category_name.lower()}?",
                "answer": f"🔍 CARACTERISTICI CHEIE: Compatibilitatea cu bicicleta, calitatea materialelor, facilitatea de instalare și întreținere. Verificați întotdeauna specificațiile tehnice și reviews-urile înainte de achiziție."
            },
            {
                "question": f"Cum știu dacă {category_name.lower()} sunt compatibile cu bicicleta mea?",
                "answer": f"🔧 VERIFICARE COMPATIBILITATE: Consultați manualul bicicletei, măsurați dimensiunile necesare, verificați standardele tehnice. În caz de dubii, contactați specialiștii noștri pentru consultanță gratuită."
            }
        ]
    
    # Adaugă informații din real_data dacă sunt disponibile
    if real_data and real_data.get('product_count', 0) > 0:
        price_info = ""
        if 'price_range' in real_data and real_data['price_range']:
            pr = real_data['price_range']
            if pr.get('min') and pr.get('max'):
                price_info = f"Prețurile variază între {pr['min']:.0f}-{pr['max']:.0f} RON. "
        
        brand_info = ""
        if 'brands' in real_data and real_data['brands']:
            brands = real_data['brands'][:3]  # Top 3 mărci
            brand_info = f"Mărci recomandate: {', '.join(brands)}. "
        
        if price_info or brand_info:
            specific_faqs.append({
                "question": f"Care sunt opțiunile disponibile și prețurile pentru {category_name.lower()}?",
                "answer": f"💰 {price_info}{brand_info}Avem {real_data.get('product_count', 'mai multe')} produse în stoc cu livrare rapidă și garanție."
            })
    
    return specific_faqs

def clean_category_faqs(data):
    """Curăță FAQ-urile din toate categoriile"""
    
    cleaned_count = 0
    categories_list = data.get('categories', [])
    total_categories = len(categories_list)
    
    for category_data in categories_list:
        category_id = category_data.get('id', '')
        category_name = category_data.get('name', category_id)
        
        # Verifică în schema_markup și faq_data
        schema_updated = False
        faq_updated = False
        
        # Curăță schema_markup FAQ
        if 'content_structure' in category_data and 'schema_markup' in category_data['content_structure']:
            schema = category_data['content_structure']['schema_markup']
            if 'faq_page' in schema and 'mainEntity' in schema['faq_page']:
                main_entities = schema['faq_page']['mainEntity']
                original_count = len(main_entities)
                
                # Filtrează întrebările generice
                filtered_entities = [
                    entity for entity in main_entities 
                    if not is_generic_question(entity.get('name', ''))
                ]
                
                if len(filtered_entities) < original_count:
                    # Generează FAQ-uri specifice
                    real_data = category_data.get('real_data')
                    specific_faqs = generate_specific_faqs(category_id, category_name, real_data)
                    
                    # Convertește la format schema
                    new_entities = []
                    for faq in specific_faqs:
                        new_entities.append({
                            "@type": "Question",
                            "name": faq["question"],
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": faq["answer"]
                            }
                        })
                    
                    # Păstrează FAQ-urile specifice existente și adaugă noile
                    schema['faq_page']['mainEntity'] = filtered_entities + new_entities
                    schema_updated = True
        
        # Curăță faq_data
        if 'content_structure' in category_data and 'faq_data' in category_data['content_structure']:
            faq_data = category_data['content_structure']['faq_data']
            original_count = len(faq_data)
            
            # Filtrează întrebările generice
            filtered_faqs = [
                faq for faq in faq_data 
                if not is_generic_question(faq.get('question', ''))
            ]
            
            if len(filtered_faqs) < original_count:
                # Generează FAQ-uri specifice
                real_data = category_data.get('real_data')
                specific_faqs = generate_specific_faqs(category_id, category_name, real_data)
                
                # Înlocuiește FAQ-urile
                category_data['content_structure']['faq_data'] = filtered_faqs + specific_faqs
                faq_updated = True
        
        if schema_updated or faq_updated:
            cleaned_count += 1
            print(f"✅ Actualizat: {category_id}")
        
    return cleaned_count, total_categories

def main():
    """Funcția principală"""
    print("🧹 CURĂȚARE FAQ-URI GENERICE")
    print("=" * 50)
    
    # Încarcă datele
    data = load_categories()
    if not data:
        print("❌ Nu s-a putut încărca JSON-ul")
        return
    
    print(f"📊 Total categorii: {len(data.get('categories', []))}")
    
    # Curăță FAQ-urile
    cleaned_count, total_categories = clean_category_faqs(data)
    
    # Salvează rezultatele
    if save_categories(data):
        print(f"\n✅ FINALIZAT: {cleaned_count}/{total_categories} categorii actualizate")
        print("🔥 FAQ-urile generice au fost înlocuite cu conținut specific!")
    else:
        print("\n❌ Eroare la salvarea fișierului")

if __name__ == "__main__":
    main()
