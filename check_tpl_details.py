import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/ai_learning_templates.json', 'r', encoding='utf-8') as f:
    tpls = json.load(f)

for i in range(12, len(tpls)):
    t = tpls[i]
    print(i+1, t.get('id'), repr(t.get('name')), len(t.get('catalyst_rules', [])))
