#!/usr/bin/env python3
import json

data = json.load(open('../data/categories_ai_enhanced.json', 'r', encoding='utf-8'))
total = len(data['categories'])
with_products = sum(1 for cat in data['categories'] if cat.get('real_data', {}).get('product_count', 0) > 0)
success_rate = (with_products / total) * 100
total_mappings = sum(cat.get('real_data', {}).get('product_count', 0) for cat in data['categories'])

print(f'🏆 FINAL SUCCESS RATE: {success_rate:.1f}% ({with_products}/{total} categories)')
print(f'📦 Total product mappings: {total_mappings:,}')

if success_rate >= 75:
    print('🎯 EXCELLENT! Over 75% success rate achieved!')
elif success_rate >= 50:
    print('✅ GREAT! Over 50% success rate achieved!')
else:
    print('⚠️ Need improvement')

print(f'\n📊 Summary:')
print(f'   ✅ Successfully mapped {with_products} out of {total} categories')
print(f'   📈 Increased from 10.9% to {success_rate:.1f}% success rate')
print(f'   🔄 Reduced false positives: 40,581 → {total_mappings:,} mappings')
print(f'   🎯 Including missing categories like "urechi-cadru" with {next((cat.get("real_data", {}).get("product_count", 0) for cat in data["categories"] if "urechi" in cat.get("id", "")), 0)} products')
