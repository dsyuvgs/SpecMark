import json

with open('tests/agent_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data['results']
with open('tests/agent_50.txt', 'w', encoding='utf-8') as out:
    for r in results[:50]:
        out.write(f"{r['id']}|{r['text']}|{r['sentiment']}|{r['type']}|{r['priority']}|{r['source']}\n")
print(f'Exported {min(50, len(results))} items')
