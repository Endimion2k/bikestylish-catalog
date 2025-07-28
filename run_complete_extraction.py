#!/usr/bin/env python3
"""
Script pentru rularea extragerii complete în background
"""

from final_content_extractor import FinalContentExtractor

if __name__ == "__main__":
    extractor = FinalContentExtractor(
        r"c:\Users\Maia\Downloads\python\endpoint\bikestylish-catalog\data\categories_ai_enhanced.json"
    )
    
    print("🚀 Începe procesarea completă a tuturor categoriilor...")
    extractor.process_all_categories_complete()
    print("🎉 Procesare completată!")
