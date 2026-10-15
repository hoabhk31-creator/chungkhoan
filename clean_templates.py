import json

with open("data/ai_learning_templates.json", "r", encoding="utf-8") as f:
    tpls = json.load(f)

seen_ids = set()
unique_tpls = []
for t in tpls:
    tid = t.get("id")
    name = t.get("name")
    key = (tid, name)
    if key not in seen_ids:
        seen_ids.add(key)
        unique_tpls.append(t)

print(f"Original templates: {len(tpls)} -> Unique templates: {len(unique_tpls)}")
with open("data/ai_learning_templates.json", "w", encoding="utf-8") as f:
    json.dump(unique_tpls, f, ensure_ascii=False, indent=2)
print("Saved unique templates successfully.")
