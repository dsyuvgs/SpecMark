import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime

API_KEY = os.environ.get('DIFY_API_KEY', '')
BASE_URL = os.environ.get('DIFY_BASE_URL', 'https://api.dify.ai/v1/chat-messages')
TIMEOUT = 120

TEST_CASES = [
    {
        'id': 'case1',
        'name': '单条反馈分类',
        'query': '扫地机器人噪音太大，晚上被吵醒了',
        'checks': ['类型', '情绪', '优先级', '隐含需求'],
        'must_contain': ['体验', '负面', '高', '静音', '降噪'],
        'must_not_contain': ['功能问题', '性能问题'],
    },
    {
        'id': 'case2',
        'name': '单条PRD审查',
        'query': '用户登录功能：输入手机号获取验证码即可登录',
        'checks': ['风险点', '风险等级', '修改建议'],
        'must_contain': ['异常处理', '验证码', '登录'],
        'must_not_contain': [],
    },
    {
        'id': 'case3',
        'name': '场景声明',
        'query': '我是做电商的，给开发看',
        'checks': ['已记录场景', '电商'],
        'must_contain': ['电商', '开发'],
        'must_not_contain': [],
    },
    {
        'id': 'case4',
        'name': '无效输入',
        'query': '今天天气真好',
        'checks': ['请输入有效'],
        'must_contain': [],
        'must_not_contain': ['风险点', '类型：', '情绪：'],
    },
    {
        'id': 'case5',
        'name': '批量分类请求',
        'query': '帮我分类这些反馈',
        'checks': [],
        'must_contain': [],
        'must_not_contain': [],
    },
    {
        'id': 'case6',
        'name': 'PRD检查请求',
        'query': '检查',
        'checks': [],
        'must_contain': [],
        'must_not_contain': [],
    },
]


async def call_dify(session, query):
    body = {
        'inputs': {},
        'query': query,
        'response_mode': 'streaming',
        'user': 'specmark-test'
    }
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        async with session.post(BASE_URL, headers=headers, json=body,
                                timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return None, f'HTTP {resp.status}: {error_text[:300]}'

            full_answer = ''
            async for line in resp.content:
                line_text = line.decode('utf-8').strip()
                if not line_text or not line_text.startswith('data: '):
                    continue
                data_str = line_text[6:]
                if data_str.strip() == '[DONE]':
                    break
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                event_type = data.get('event', '')
                if event_type in ('message', 'agent_message'):
                    full_answer += data.get('answer', '')
                elif event_type == 'message_replace':
                    full_answer = data.get('answer', full_answer)
                elif event_type == 'error':
                    return None, data.get('message', 'unknown')

            return full_answer, None

    except asyncio.TimeoutError:
        return None, 'timeout'
    except Exception as e:
        return None, str(e)


def check_output(answer, tc):
    results = []
    all_pass = True

    for keyword in tc['must_contain']:
        if keyword in answer:
            results.append(('✅', f'包含 "{keyword}"'))
        else:
            results.append(('❌', f'缺少 "{keyword}"'))
            all_pass = False

    for keyword in tc['must_not_contain']:
        if keyword not in answer:
            results.append(('✅', f'不含 "{keyword}"'))
        else:
            results.append(('⚠️', f'意外包含 "{keyword}"'))

    return all_pass, results


async def run_tests():
    print(f'\n{"="*70}')
    print(f'  SpecMark 输出样例验证测试')
    print(f'  用例数: {len(TEST_CASES)} | {datetime.now().strftime("%H:%M:%S")}')
    print(f'{"="*70}\n')

    connector = aiohttp.TCPConnector(limit=1, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        for i, tc in enumerate(TEST_CASES):
            print(f'[{i+1}/{len(TEST_CASES)}] {tc["name"]}')
            print(f'  输入: {tc["query"][:60]}')

            start = time.time()
            answer, error = await call_dify(session, tc['query'])
            elapsed = time.time() - start

            if error:
                print(f'  ❌ 错误: {error}')
                print()
                continue

            print(f'  耗时: {elapsed:.1f}s')
            print(f'  输出预览: {answer[:120]}...')

            if tc['must_contain'] or tc['must_not_contain']:
                passed, checks = check_output(answer, tc)
                for icon, msg in checks:
                    print(f'  {icon} {msg}')
                status = '✅ 通过' if passed else '❌ 未通过'
            else:
                status = '➖ 人工检查'
                passed = True

            print(f'  结果: {status}')
            print(f'  完整输出:\n{answer[:600]}')
            print(f'  {"─"*60}\n')

    print(f'{"="*70}')
    print(f'  测试完成')
    print(f'{"="*70}\n')


if __name__ == '__main__':
    asyncio.run(run_tests())
