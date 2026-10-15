import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('data/ai_learned_catalysts.json', 'r', encoding='utf-8') as f:
    learned = json.load(f)

print(f"Total tickers in ai_learned_catalysts.json: {len(learned)}")
for tk, val in learned.items():
    cats = val.get('catalysts', [])
    risks = val.get('risks', [])
    print(f"- {tk:5}: Catalysts={len(cats):2}, Risks={len(risks):2}")
