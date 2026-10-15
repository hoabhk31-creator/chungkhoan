import json

with open("data/ai_learning_templates.json", "r", encoding="utf-8") as f:
    tpls = json.load(f)

# Keep standard templates and only 1 custom if unique
cleaned = []
seen_names = set()
for t in tpls:
    name = t.get("name")
    if name in seen_names and str(t.get("id")).startswith("custom-"):
        continue
    seen_names.add(name)
    cleaned.append(t)

print(f"Cleaned templates: {len(cleaned)}")
with open("data/ai_learning_templates.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)
