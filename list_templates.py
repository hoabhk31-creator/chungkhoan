import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('data/ai_learning_templates.json', 'r', encoding='utf-8') as f:
    tpls = json.load(f)

for i, t in enumerate(tpls):
    name = t.get('name')
    kws = t.get('keywords', [])
    print(f"{i+1}. {name} | Keywords count: {len(kws)}")
    print(f"   Keywords sample: {kws[:6]}")
