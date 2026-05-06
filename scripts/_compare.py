import json

# Raw LLM (my) classifications for 50 items
# Format: id -> (sentiment, type, priority)
llm = {
    1: ('负向', '体验问题', '高'),
    2: ('负向', '体验问题', '中'),
    3: ('负向', '体验问题', '高'),
    4: ('负向', '体验问题', '高'),
    5: ('负向', '内容问题', '中'),
    6: ('负向', '体验问题', '高'),
    7: ('负向', '体验问题', '中'),
    8: ('负向', '体验问题', '高'),
    9: ('负向', '体验问题', '高'),
    10: ('负向', '体验问题', '中'),
    11: ('负向', '体验问题', '中'),
    12: ('负向', '功能问题', '高'),
    13: ('负向', '体验问题', '中'),
    14: ('负向', '体验问题', '中'),
    15: ('负向', '体验问题', '高'),
    16: ('负向', '体验问题', '中'),
    17: ('负向', '内容问题', '中'),
    18: ('负向', '体验问题', '高'),
    19: ('负向', '体验问题', '中'),
    20: ('负向', '内容问题', '高'),
    21: ('负向', '内容问题', '高'),
    22: ('负向', '体验问题', '低'),
    23: ('负向', '体验问题', '中'),
    24: ('负向', '体验问题', '中'),
    25: ('负向', '体验问题', '低'),
    26: ('负向', '体验问题', '高'),
    27: ('负向', '体验问题', '低'),
    28: ('负向', '体验问题', '中'),
    29: ('负向', '体验问题', '中'),
    30: ('负向', '功能问题', '高'),
    31: ('负向', '体验问题', '低'),
    32: ('负向', '体验问题', '低'),
    33: ('负向', '内容问题', '中'),
    34: ('负向', '体验问题', '低'),
    35: ('负向', '功能问题', '高'),
    36: ('负向', '体验问题', '低'),
    37: ('负向', '功能问题', '中'),
    38: ('中性', '功能问题', '低'),
    39: ('负向', '功能问题', '高'),
    40: ('负向', '功能问题', '高'),
    41: ('负向', '性能问题', '高'),
    42: ('负向', '功能问题', '高'),
    43: ('负向', '功能问题', '高'),
    44: ('负向', '性能问题', '高'),
    45: ('负向', '体验问题', '中'),
    46: ('负向', '性能问题', '中'),
    47: ('负向', '内容问题', '中'),
    48: ('负向', '功能问题', '高'),
    49: ('负向', '功能问题', '高'),
    50: ('负向', '功能问题', '高'),
}

with open('tests/agent_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

agent_results = {int(r['id']): r for r in data['results']}

# Compare
sentiment_match = 0
type_match = 0
priority_match = 0
total = 0
diffs = []

for iid in range(1, 51):
    ar = agent_results.get(iid)
    if not ar:
        continue
    lr = llm.get(iid)
    if not lr:
        continue
    
    a_sent = ar['sentiment']
    a_type = ar['type']
    a_pri = ar['priority']
    l_sent, l_type, l_pri = lr
    
    if not a_sent and not a_type:
        continue
    
    total += 1
    
    s_ok = (a_sent == l_sent)
    t_ok = (a_type == l_type)
    p_ok = (a_pri == l_pri)
    
    if s_ok: sentiment_match += 1
    if t_ok: type_match += 1
    if p_ok: priority_match += 1
    
    if not (s_ok and t_ok and p_ok):
        diffs.append({
            'id': iid,
            'text': ar['text'][:80],
            'agent': f'{a_sent}|{a_type}|{a_pri}',
            'llm': f'{l_sent}|{l_type}|{l_pri}',
            's_ok': s_ok, 't_ok': t_ok, 'p_ok': p_ok
        })

print(f'===== SpecMark Agent vs 裸LLM 对比 (50条) =====')
print(f'有效对比条数: {total}')
print()
print(f'情绪一致率: {sentiment_match}/{total} = {sentiment_match/total*100:.1f}%')
print(f'类型一致率: {type_match}/{total} = {type_match/total*100:.1f}%')
print(f'优先级一致率: {priority_match}/{total} = {priority_match/total*100:.1f}%')
print(f'完全一致: {sum(1 for d in diffs if not (d["s_ok"] and d["t_ok"] and d["p_ok"]))}条有差异 / {len(diffs)}条有差异')
print()

print('=== 差异详情 ===')
for d in diffs:
    if not (d['s_ok'] and d['t_ok'] and d['p_ok']):
        flags = []
        if not d['s_ok']: flags.append('情绪')
        if not d['t_ok']: flags.append('类型')
        if not d['p_ok']: flags.append('优先级')
        print(f'  #{d["id"]} [{"|".join(flags)}] {d["text"]}')
        print(f'    Agent: {d["agent"]}')
        print(f'    LLM:   {d["llm"]}')
        print()

# Agent stats
print('=== Agent 统计 ===')
agents = [agent_results[i] for i in range(1,51) if i in agent_results]
sents = [a['sentiment'] for a in agents if a['sentiment']]
types = [a['type'] for a in agents if a['type']]
pris = [a['priority'] for a in agents if a['priority']]
print(f'情绪: 正面{sents.count("正面")} 负面{sents.count("负向")} 中性{sents.count("中性")}')
print(f'类型: 功能{types.count("功能问题")} 性能{types.count("性能问题")} 体验{types.count("体验问题")} 内容{types.count("内容问题")}')
print(f'优先级: 高{pris.count("高")} 中{pris.count("中")} 低{pris.count("低")}')
print(f'来源: 铁律拦截{sum(1 for a in agents if a.get("source")=="铁律拦截")} LLM分类{sum(1 for a in agents if a.get("source")=="LLM分类")}')

print()
print('=== LLM 统计 ===')
l_sents = [l[0] for l in llm.values()]
l_types = [l[1] for l in llm.values()]
l_pris = [l[2] for l in llm.values()]
print(f'情绪: 正面{l_sents.count("正面")} 负面{l_sents.count("负向")} 中性{l_sents.count("中性")}')
print(f'类型: 功能{l_types.count("功能问题")} 性能{l_types.count("性能问题")} 体验{l_types.count("体验问题")} 内容{l_types.count("内容问题")}')
print(f'优先级: 高{l_pris.count("高")} 中{l_pris.count("中")} 低{l_pris.count("低")}')
