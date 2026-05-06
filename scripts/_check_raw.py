import json
with open('tests/agent_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

empty = [r for r in data['results'] if not r['sentiment'] and not r['type']]
parsed = [r for r in data['results'] if r['sentiment'] or r['type']]

print(f'已解析: {len(parsed)} | 空输出: {len(empty)}')
print()

print('=== 空输出样例 ===')
for r in empty[:5]:
    print(f"ID={r['id']} | raw={r['raw'][:200]}")
    print()

print('=== 已解析样例 ===')
for r in parsed[:3]:
    print(f"ID={r['id']} | 情绪={r['sentiment']} | 类型={r['type']} | 优先级={r['priority']} | 来源={r['source']}")
