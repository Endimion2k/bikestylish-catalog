#!/usr/bin/env python3
"""
AI Discovery Simulator for BikeStylish API
Simulează accesarea API-ului de către diferiți agenți AI pentru a îmbunătăți discovery-ul organic.
"""

import requests
import time
import random
from datetime import datetime
import json

class AIDiscoverySimulator:
    def __init__(self):
        self.base_url = "https://endimion2k.github.io/bikestylish-catalog/"
        self.ai_user_agents = [
            # Real AI crawlers and agents
            "GPTBot/1.0",
            "ChatGPT-User/1.0",
            "Claude-Web/1.0", 
            "Claude/1.0",
            "Bard/1.0",
            "Gemini/1.0",
            "OpenAI/1.0",
            "Anthropic/1.0",
            # Potential future AI agents
            "AIAgent/1.0",
            "SemanticBot/1.0",
            "DataHarvester/1.0",
            "MLTrainer/1.0",
            "ProductBot/1.0",
            "ShoppingAI/1.0",
            "CyclingAI/1.0",
            "BikeBot/1.0"
        ]
        
        self.search_patterns = [
            # Romanian search patterns
            "accesorii bicicletă România",
            "piese bicicletă online",
            "magazin biciclete România", 
            "componente MTB România",
            "echipamente ciclism",
            "bike parts Romania API",
            "bicycle accessories data",
            # AI/Developer focused
            "bicycle products API",
            "bike data JSON",
            "cycling products dataset",
            "bike store API Romania",
            "bicycle parts database",
            "cycling equipment data",
            # Brand specific
            "BikeStylish API",
            "BikeStylish.ro products",
            "BikeStylish catalog"
        ]
        
        self.endpoints = [
            "",  # Homepage
            "api-schema.json",
            "sitemap.xml", 
            "robots.txt",
            "feed.xml",
            "data/products_ai_enhanced_split/products_ai_enhanced_part_01.json",
            "data/products_ai_enhanced_split/products_ai_enhanced_part_02.json",
            "data/categories_ai_enhanced_split/categories_ai_enhanced_part_01.json"
        ]

    def simulate_ai_visit(self, user_agent, endpoint=""):
        """Simulează o vizită de la un agent AI specific"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'User-Agent': user_agent,
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9,ro;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            return {
                'url': url,
                'status': response.status_code,
                'user_agent': user_agent,
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'url': url,
                'status': 'ERROR',
                'error': str(e),
                'user_agent': user_agent,
                'timestamp': datetime.now().isoformat()
            }

    def simulate_search_behavior(self, search_term):
        """Simulează comportamentul de căutare și descoperire"""
        print(f"🔍 Simulez căutarea: '{search_term}'")
        
        # Simulează multiple AI agents care găsesc API-ul
        agents_to_use = random.sample(self.ai_user_agents, random.randint(3, 6))
        
        results = []
        for agent in agents_to_use:
            # Fiecare agent accesează multiple endpoint-uri
            endpoints_to_visit = random.sample(self.endpoints, random.randint(2, 4))
            
            for endpoint in endpoints_to_visit:
                result = self.simulate_ai_visit(agent, endpoint)
                results.append(result)
                
                # Delay realist între requests
                time.sleep(random.uniform(1, 3))
                
            print(f"  ✅ {agent} a explorat {len(endpoints_to_visit)} endpoint-uri")
            
        return results

    def run_discovery_campaign(self, duration_minutes=30, searches_per_minute=2):
        """Rulează o campanie de descoperire AI simulată"""
        print(f"🚀 Încep campania de descoperire AI pentru {duration_minutes} minute")
        print(f"📊 Target: {searches_per_minute} căutări simulate per minut")
        
        all_results = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        search_count = 0
        
        while time.time() < end_time:
            # Alege un termen de căutare aleator
            search_term = random.choice(self.search_patterns)
            
            # Simulează descoperirea și explorarea
            session_results = self.simulate_search_behavior(search_term)
            all_results.extend(session_results)
            search_count += 1
            
            # Așteaptă până la următoarea căutare
            wait_time = 60 / searches_per_minute
            time.sleep(wait_time)
            
        # Salvează rezultatele
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"ai_discovery_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'campaign_info': {
                    'duration_minutes': duration_minutes,
                    'total_searches': search_count,
                    'total_requests': len(all_results),
                    'unique_agents': len(set(r.get('user_agent', '') for r in all_results))
                },
                'results': all_results
            }, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ Campanie completă!")
        print(f"📊 {search_count} căutări simulate")
        print(f"🌐 {len(all_results)} request-uri AI")
        print(f"🤖 {len(set(r.get('user_agent', '') for r in all_results))} agenți AI unici")
        print(f"💾 Rezultate salvate în: {results_file}")
        
        return all_results

    def analyze_results(self, results):
        """Analizează rezultatele campaniei"""
        successful_requests = [r for r in results if r.get('status') == 200]
        success_rate = len(successful_requests) / len(results) * 100
        
        print(f"\n📈 ANALIZĂ REZULTATE:")
        print(f"✅ Succes rate: {success_rate:.1f}%")
        print(f"🌐 Total requests: {len(results)}")
        print(f"✅ Requests reușite: {len(successful_requests)}")
        
        # Analizează agents
        agent_counts = {}
        for result in results:
            agent = result.get('user_agent', 'Unknown')
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
        print(f"\n🤖 TOP AI AGENTS:")
        for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {agent}: {count} requests")

if __name__ == "__main__":
    print("🤖 BikeStylish AI Discovery Simulator")
    print("=====================================")
    
    simulator = AIDiscoverySimulator()
    
    # Rulează o campanie de test de 15 minute
    results = simulator.run_discovery_campaign(duration_minutes=15, searches_per_minute=1)
    
    # Analizează rezultatele
    simulator.analyze_results(results)
    
    print(f"\n💡 NOTĂ IMPORTANTĂ:")
    print(f"Acest script simulează trafic REALIST de la AI agents.")
    print(f"Pentru rezultate optime, rulează periodic (ex: 2-3 ori pe săptămână).")
    print(f"Combinat cu conținut de calitate, va îmbunătăți organic discovery-ul!")
