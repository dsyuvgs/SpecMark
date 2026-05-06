import asyncio, aiohttp, json

API_KEY = 'app-7D4eJnQygDHJFFSmda4YbURl'
BASE_URL = 'https://api.dify.ai/v1/chat-messages'

async def debug(query, label):
    body = {'inputs': {}, 'query': query, 'response_mode': 'streaming', 'user': 'debug'}
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    
    async with aiohttp.ClientSession() as s:
        async with s.post(BASE_URL, headers=headers, json=body, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            print(f'=== {label} ===')
            print(f'  query: {query[:80]}...')
            async for line in resp.content:
                text = line.decode('utf-8').strip()
                if text.startswith('data: '):
                    data_str = text[6:]
                    if data_str == '[DONE]': break
                    try:
                        d = json.loads(data_str)
                        ev = d.get('event', '?')
                        if ev == 'node_started':
                            nd = d.get('data', {})
                            print(f'  [START] {nd.get("title", "?")}')
                        elif ev == 'node_finished':
                            nd = d.get('data', {})
                            title = nd.get('title', '?')
                            err = nd.get('error', '')
                            outputs = nd.get('outputs', {})
                            if err:
                                print(f'  [{title}] ERROR: {err[:300]}')
                            elif outputs:
                                out_str = json.dumps(outputs, ensure_ascii=False)[:500]
                                print(f'  [{title}] outputs={out_str}')
                            else:
                                print(f'  [{title}] OK (no outputs)')
                        elif ev == 'workflow_finished':
                            data = d.get('data', {})
                            outputs = data.get('outputs', {})
                            status = data.get('status', '?')
                            err = data.get('error', '')
                            print(f'  [FINISHED] status={status}')
                            if outputs:
                                print(f'  [OUTPUT] {json.dumps(outputs, ensure_ascii=False)[:500]}')
                            if err:
                                print(f'  [ERROR] {err[:300]}')
                    except Exception as e:
                        print(f'  PARSE_ERR: {e}')
            print()

async def main():
    # Test a few samples that were classified as invalid_input
    samples = [
        ('骑手未经过本人同意，擅自将餐品放在驿站、快递柜、门口，导致餐品丢失、错拿，联系平台与商家后，双方互相推诿，无法及时解决问题', 'Case1-外卖配送'),
        ('收到的外卖餐品中出现异物、餐品变质腐坏，食用后出现肠胃不适', 'Case2-食品安全'),
        ('在京东外卖点餐，食用时发现餐品内有寄生虫，与商家、平台沟通维权，对方拒不按法律规定赔偿', 'Case3-食品安全'),
    ]
    for query, label in samples:
        await debug(query, label)

asyncio.run(main())
