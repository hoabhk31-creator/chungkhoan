import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('data/ai_learning_history.json', 'r', encoding='utf-8') as f:
    history = json.load(f)

print(f"Total history entries: {len(history)}")
tickers_in_history = set(h.get('ticker') for h in history if h.get('ticker'))
print(f"Unique tickers ({len(tickers_in_history)}):", sorted(list(tickers_in_history)))

missing_total_count = sum(1 for h in history if h.get('total_knowledge_catalysts') is None)
print(f"Entries missing total_knowledge_catalysts: {missing_total_count}")

# Check sample entries
for h in history[:6]:
    print(f"- {h.get('ticker')}: {h.get('title')[:45]}... | Extracted: {h.get('catalysts_extracted')} | Total: {h.get('total_knowledge_catalysts')}")
