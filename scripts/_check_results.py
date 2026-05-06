import json
with open('tests/agent_results.json','r',encoding='utf-8') as f:
    data = json.load(f)
results = data['results']
empty = [r for r in results if not r['sentiment'] and not r['type']]
classified = [r for r in results if r['sentiment'] or r['type']]
print(f'有分类: {len(classified)} | 空输出: {len(empty)}')
print()
print('=== 空输出样例(前5条) ===')
for r in empty[:5]:
    print(f'ID={r["id"]} | text={r["text"][:100]}')
    print(f'  raw={r["raw"][:200]}')
    print()
print('=== 有分类样例(全部) ===')
for r in classified:
    print(f'ID={r["id"]} | 情绪={r["sentiment"]} | 类型={r["type"]} | 优先级={r["priority"]} | 来源={r["source"]}')
    print(f'  text={r["text"][:100]}')
