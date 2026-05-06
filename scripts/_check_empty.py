import json
with open('tests/agent_results.json','r',encoding='utf-8') as f:
    data = json.load(f)
results = data['results']
empty = [r for r in results if not r['sentiment'] and not r['type']]
valid = [r for r in results if r['sentiment'] or r['type']]
print(f'总数: {len(results)} | 有效: {len(valid)} | 空: {len(empty)}')
sources = [r.get('source','') for r in valid]
iron = sources.count('铁律拦截')
llm_src = sources.count('LLM分类')
print(f'来源: 铁律拦截{iron} LLM分类{llm_src} 其他{len(sources)-iron-llm_src}')
print()
print('空输出项:')
for r in empty:
    print(f'  #{r["id"]} {r["text"][:80]}')
