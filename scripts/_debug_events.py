import asyncio, aiohttp, json

API_KEY = 'app-7D4eJnQygDHJFFSmda4YbURl'
BASE_URL = 'https://api.dify.ai/v1/chat-messages'

async def debug(query, label):
    body = {'inputs': {}, 'query': query, 'response_mode': 'streaming', 'user': 'debug'}
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    
    async with aiohttp.ClientSession() as s:
        async with s.post(BASE_URL, headers=headers, json=body, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            print(f'=== {label} ===')
            async for line in resp.content:
                text = line.decode('utf-8').strip()
                if text.startswith('data: '):
                    data_str = text[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        d = json.loads(data_str)
                        ev = d.get('event', '?')
                        if ev == 'node_finished':
                            nd = d.get('data', {})
                            title = nd.get('title', '?')
                            status = nd.get('status', '?')
                            err = nd.get('error', '')
                            outputs = nd.get('outputs', {})
                            if err:
                                print(f'  [node_finished] {title} ERROR: {str(err)[:200]}')
                            elif outputs:
                                out_str = json.dumps(outputs, ensure_ascii=False)[:200]
                                print(f'  [node_finished] {title} outputs={out_str}')
                            else:
                                print(f'  [node_finished] {title} status={status}')
                        elif ev == 'workflow_finished':
                            data = d.get('data', {})
                            outputs = data.get('outputs', {})
                            status = data.get('status', '?')
                            err = data.get('error', '')
                            err_str = err[:200] if err else ''
                            print(f'  [workflow_finished] status={status} outputs={outputs} err={err_str}')
                        elif ev == 'message':
                            ans = d.get('answer', '')
                            if ans:
                                print(f'  [message] {ans[:300]}')
                    except Exception as e:
                        print(f'  ERR: {e}')
            print()

asyncio.run(debug('扫地机器人噪音太大，晚上被吵醒了', 'Case1-反馈分类'))
