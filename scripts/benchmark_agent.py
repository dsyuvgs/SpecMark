import asyncio, aiohttp, json, csv, time, os, re
from datetime import datetime

API_KEY = 'app-7D4eJnQygDHJFFSmda4YbURl'
BASE_URL = 'https://api.dify.ai/v1/chat-messages'
CONCURRENCY = 1
TIMEOUT = 120

def load_feedback(filepath, limit=100):
    items = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append({
                'id': row['序号'],
                'text': row['反馈内容'],
                'category': row.get('品类', '')
            })
            if len(items) >= limit:
                break
    return items

async def call_agent(session, text, semaphore):
    async with semaphore:
        await asyncio.sleep(2)
        body = {'inputs': {}, 'query': text, 'response_mode': 'streaming', 'user': 'benchmark'}
        headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
        try:
            async with session.post(BASE_URL, headers=headers, json=body,
                                    timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as resp:
                if resp.status != 200:
                    return None, f'HTTP {resp.status}', 0
                full = ''
                async for line in resp.content:
                    t = line.decode('utf-8').strip()
                    if t.startswith('data: '):
                        ds = t[6:]
                        if ds == '[DONE]': break
                        try:
                            d = json.loads(ds)
                            if d.get('event') in ('message', 'agent_message'):
                                full += d.get('answer', '')
                        except: pass
                return full, None, 0
        except Exception as e:
            return None, str(e), 0

def parse_result(answer):
    r = {'sentiment': '', 'type': '', 'priority': '', 'need': '', 'core': '', 'tags': '', 'source': ''}
    if not answer: return r
    m = re.search(r'情绪[：:]\s*(.+)', answer)
    if m: r['sentiment'] = m.group(1).strip()
    m = re.search(r'类型[：:]\s*(.+)', answer)
    if m: r['type'] = m.group(1).strip()
    m = re.search(r'优先级[：:]\s*(.+)', answer)
    if m: r['priority'] = m.group(1).strip()
    m = re.search(r'隐含需求[：:]\s*(.+)', answer)
    if m: r['need'] = m.group(1).strip()
    m = re.search(r'核心功能[：:]\s*(.+)', answer)
    if m: r['core'] = m.group(1).strip()
    m = re.search(r'用户标签[：:]\s*(.+)', answer)
    if m: r['tags'] = m.group(1).strip()
    m = re.search(r'来源[：:]\s*(.+)', answer)
    if m: r['source'] = m.group(1).strip()
    return r

async def main():
    items = load_feedback(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'test_set_300.csv'), 100)
    sem = asyncio.Semaphore(CONCURRENCY)
    
    print(f'SpecMark Agent 基准测试 - {len(items)}条')
    print(f'开始: {datetime.now().strftime("%H:%M:%S")}\n')
    
    t0 = time.time()
    results = []
    connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as s:
        tasks = [call_agent(s, it['text'], sem) for it in items]
        raw = await asyncio.gather(*tasks)
    
    total_time = time.time() - t0
    
    for i, (item, (answer, err, _)) in enumerate(zip(items, raw)):
        parsed = parse_result(answer) if answer else {}
        results.append({
            'id': item['id'],
            'text': item['text'][:80],
            'category': item['category'],
            'sentiment': parsed.get('sentiment', ''),
            'type': parsed.get('type', ''),
            'priority': parsed.get('priority', ''),
            'need': parsed.get('need', ''),
            'core': parsed.get('core', ''),
            'tags': parsed.get('tags', ''),
            'source': parsed.get('source', ''),
            'error': err or '',
            'raw': (answer or '')[:300]
        })
        if (i+1) % 20 == 0:
            print(f'  进度: {i+1}/{len(items)}')
    
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'agent_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'total_time': total_time, 'count': len(items), 'results': results}, f, ensure_ascii=False, indent=2)
    
    errors = [r for r in results if r['error']]
    success = [r for r in results if not r['error']]
    sentiments = [r['sentiment'] for r in success if r['sentiment']]
    priorities = [r['priority'] for r in success if r['priority']]
    types = [r['type'] for r in success if r['type']]
    sources = [r['source'] for r in success if r['source']]
    
    print(f'\n===== SpecMark Agent 结果 =====')
    print(f'总数: {len(items)} | 成功: {len(success)} | 失败: {len(errors)}')
    print(f'总耗时: {total_time:.1f}s | 平均: {total_time/len(items):.1f}s/条')
    print(f'情绪分布: 正面{sentiments.count("正面")} 负面{sentiments.count("负向")} 中性{sentiments.count("中性")}')
    print(f'优先级分布: 高{priorities.count("高")} 中{priorities.count("中")} 低{priorities.count("低")}')
    print(f'类型分布: 功能{types.count("功能问题")} 性能{types.count("性能问题")} 体验{types.count("体验问题")} 内容{types.count("内容问题")}')
    print(f'来源分布: 铁律拦截{sources.count("铁律拦截")} LLM分类{sources.count("LLM分类")}')
    print(f'结果已保存: {out_path}')

if __name__ == '__main__':
    asyncio.run(main())
