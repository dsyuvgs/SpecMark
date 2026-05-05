import asyncio
import aiohttp
import json
import time
import os
import sys
from datetime import datetime

API_KEY = os.environ.get('DIFY_API_KEY', '')
BASE_URL = os.environ.get('DIFY_BASE_URL', 'https://api.dify.ai/v1/chat-messages')
EVAL_SET = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'eval_set.json')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests')

CONCURRENCY = 5
MAX_RETRIES = 2
TIMEOUT = 120


def parse_output(answer):
    if not answer:
        return {}
    result = {}
    for line in answer.split('\n'):
        line = line.strip()
        if '：' in line:
            key, val = line.split('：', 1)
            key = key.strip()
            val = val.strip()
            if key == '类型':
                result['type'] = val
            elif key == '情绪':
                result['sentiment'] = val
            elif key == '优先级':
                result['priority'] = val
            elif key == '隐含需求':
                result['implicit_need'] = val
            elif key == '用户标签':
                result['user_tag'] = val
    return result


def detect_route(answer):
    if not answer:
        return 'unknown'
    if any(k in answer for k in ['风险点', '风险等级', '🔴', '🟡', '🟢',
                                  '修改建议', '行业参考', 'Jira任务']):
        return 'prd_check'
    if '已记录场景' in answer:
        return 'scene_declare'
    if any(k in answer for k in ['类型：', '情绪：', '优先级：']):
        return 'feedback_classify'
    if '请输入有效' in answer:
        return 'invalid_input'
    if any(k in answer for k in ['风险', 'P1', 'P2', 'P3']):
        return 'prd_check'
    return 'unknown'


async def call_dify(session, query, semaphore):
    async with semaphore:
        body = {
            'inputs': {},
            'query': query,
            'response_mode': 'streaming',
            'user': 'specmark-eval'
        }
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }

        for attempt in range(MAX_RETRIES + 1):
            try:
                async with session.post(BASE_URL, headers=headers, json=body,
                                        timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as resp:
                    if resp.status == 429:
                        await asyncio.sleep(5)
                        continue
                    if resp.status != 200:
                        error_text = await resp.text()
                        if attempt < MAX_RETRIES:
                            await asyncio.sleep(3 * (attempt + 1))
                            continue
                        return None, f'HTTP {resp.status}: {error_text[:200]}'

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
                            if attempt < MAX_RETRIES:
                                await asyncio.sleep(3 * (attempt + 1))
                                break
                            return None, data.get('message', 'unknown')

                    if full_answer.strip():
                        return full_answer, None
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(5)
                        continue
                    return full_answer, 'empty_response'

            except asyncio.TimeoutError:
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(5)
                    continue
                return None, 'timeout'
            except Exception as e:
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(3)
                    continue
                return None, str(e)

        return None, 'max_retries_exceeded'


async def process_case(session, tc, semaphore, progress, total):
    query = tc['query']
    start_time = time.time()

    answer, error = await call_dify(session, query, semaphore)
    elapsed = time.time() - start_time

    if error:
        result = {**tc, 'raw_output': '', 'error': error, 'elapsed': elapsed,
                  'detected_route': 'error', 'parsed_type': '', 'parsed_sentiment': '',
                  'parsed_priority': '', 'parsed_implicit_need': '', 'parsed_user_tag': ''}
    else:
        detected_route = detect_route(answer)
        parsed = parse_output(answer) if detected_route == 'feedback_classify' else {}
        result = {**tc, 'raw_output': answer[:800], 'error': '', 'elapsed': elapsed,
                  'detected_route': detected_route,
                  'parsed_type': parsed.get('type', ''),
                  'parsed_sentiment': parsed.get('sentiment', ''),
                  'parsed_priority': parsed.get('priority', ''),
                  'parsed_implicit_need': parsed.get('implicit_need', ''),
                  'parsed_user_tag': parsed.get('user_tag', '')}

    progress['done'] += 1
    done = progress['done']

    route_ok = result['detected_route'] == tc['expected_route']
    status = '✅' if route_ok else '❌'
    if error:
        status = '⚠️'

    print(f'  [{done}/{total}] {tc["id"]} {status} '
          f'路由={result["detected_route"][:12]} '
          f'情绪={result.get("parsed_sentiment", "?")[:4]} '
          f'优先级={result.get("parsed_priority", "?")[:2]} '
          f'| {elapsed:.1f}s')

    return result


async def run_eval(cases):
    total = len(cases)
    semaphore = asyncio.Semaphore(CONCURRENCY)
    progress = {'done': 0, 'start': time.time()}

    print(f'\n{"="*70}')
    print(f'  SpecMark 四维度评测')
    print(f'  用例数: {total} | 并发: {CONCURRENCY} | {datetime.now().strftime("%H:%M:%S")}')
    print(f'{"="*70}\n')

    connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [process_case(session, tc, semaphore, progress, total) for tc in cases]
        results = await asyncio.gather(*tasks)

    total_time = time.time() - progress['start']
    return list(results), total_time


def generate_report(results, total_time):
    total = len(results)
    errors = [r for r in results if r['error']]
    success = [r for r in results if not r['error']]

    route_results = []
    for r in success:
        ok = r['detected_route'] == r['expected_route']
        route_results.append({'id': r['id'], 'ok': ok,
                              'expected': r['expected_route'], 'actual': r['detected_route']})

    route_correct = sum(1 for r in route_results if r['ok'])

    fb_cases = [r for r in success if r['expected_route'] == 'feedback_classify']
    sentiment_ok = 0
    type_ok = 0
    priority_ok = 0
    for r in fb_cases:
        if r['expected_sentiment'] and r['expected_sentiment'] in r['parsed_sentiment']:
            sentiment_ok += 1
        if r['expected_type'] and any(t in r['parsed_type'] for t in r['expected_type'].split('/')):
            type_ok += 1
        if r['expected_priority'] and r['expected_priority'] in r['parsed_priority']:
            priority_ok += 1

    fb_with_expect = [r for r in fb_cases if r['expected_sentiment']]
    fb_type_expect = [r for r in fb_cases if r['expected_type']]
    fb_pri_expect = [r for r in fb_cases if r['expected_priority']]

    avg_time = sum(r['elapsed'] for r in results if not r['error']) / max(len(success), 1)

    report = []
    report.append('# SpecMark 四维度评测报告')
    report.append('')
    report.append(f'> 测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}  ')
    report.append(f'> 用例数: {total} | 成功: {len(success)} | 失败: {len(errors)}  ')
    report.append(f'> 总耗时: {total_time:.1f}s | 平均: {avg_time:.1f}s/条  ')
    report.append('')
    report.append('---')
    report.append('')

    report.append('## 一、功能正确性')
    report.append('')
    report.append('### 1.1 路由准确率')
    report.append('')
    report.append(f'| 指标 | 结果 |')
    report.append(f'|------|------|')
    report.append(f'| 路由准确率 | {route_correct}/{len(success)} ({route_correct/max(len(success),1)*100:.1f}%) |')
    report.append('')
    report.append('### 1.2 反馈分类准确率')
    report.append('')
    report.append(f'| 指标 | 结果 |')
    report.append(f'|------|------|')
    report.append(f'| 情绪准确率 | {sentiment_ok}/{len(fb_with_expect)} ({sentiment_ok/max(len(fb_with_expect),1)*100:.1f}%) |')
    report.append(f'| 问题类型准确率 | {type_ok}/{len(fb_type_expect)} ({type_ok/max(len(fb_type_expect),1)*100:.1f}%) |')
    report.append(f'| 优先级准确率 | {priority_ok}/{len(fb_pri_expect)} ({priority_ok/max(len(fb_pri_expect),1)*100:.1f}%) |')
    report.append('')

    report.append('### 1.3 路由错误详情')
    report.append('')
    route_errors = [r for r in route_results if not r['ok']]
    if route_errors:
        report.append('| ID | 期望路由 | 实际路由 |')
        report.append('|-----|---------|---------|')
        for r in route_errors:
            report.append(f'| {r["id"]} | {r["expected"]} | {r["actual"]} |')
    else:
        report.append('无路由错误 ✅')
    report.append('')

    report.append('### 1.4 反馈分类错误详情')
    report.append('')
    fb_errors = []
    for r in fb_cases:
        issues = []
        if r['expected_sentiment'] and r['expected_sentiment'] not in r['parsed_sentiment']:
            issues.append(f'情绪:期望{r["expected_sentiment"]}实际{r["parsed_sentiment"]}')
        if r['expected_type'] and not any(t in r['parsed_type'] for t in r['expected_type'].split('/')):
            issues.append(f'类型:期望{r["expected_type"]}实际{r["parsed_type"]}')
        if r['expected_priority'] and r['expected_priority'] not in r['parsed_priority']:
            issues.append(f'优先级:期望{r["expected_priority"]}实际{r["parsed_priority"]}')
        if issues:
            fb_errors.append({'id': r['id'], 'query': r['query'][:40], 'issues': '; '.join(issues)})
    if fb_errors:
        report.append('| ID | 输入 | 问题 |')
        report.append('|-----|------|------|')
        for e in fb_errors:
            report.append(f'| {e["id"]} | {e["query"]} | {e["issues"]} |')
    else:
        report.append('无分类错误 ✅')
    report.append('')

    report.append('## 二、边界鲁棒性')
    report.append('')
    boundary_cases = [r for r in results if r['dimension'] == '边界鲁棒性']
    boundary_ok = sum(1 for r in boundary_cases if not r['error'] and r['detected_route'] == r['expected_route'])
    report.append(f'| 指标 | 结果 |')
    report.append(f'|------|------|')
    report.append(f'| 边界用例数 | {len(boundary_cases)} |')
    report.append(f'| 路由正确 | {boundary_ok}/{len(boundary_cases)} ({boundary_ok/max(len(boundary_cases),1)*100:.1f}%) |')
    report.append(f'| 错误/崩溃 | {sum(1 for r in boundary_cases if r["error"])} |')
    report.append('')

    report.append('## 三、性能效率')
    report.append('')
    times = [r['elapsed'] for r in success]
    times.sort()
    p50 = times[len(times) // 2] if times else 0
    p90 = times[int(len(times) * 0.9)] if times else 0
    p99 = times[int(len(times) * 0.99)] if times else 0
    report.append(f'| 指标 | 结果 |')
    report.append(f'|------|------|')
    report.append(f'| 平均响应时间 | {avg_time:.1f}s |')
    report.append(f'| P50 | {p50:.1f}s |')
    report.append(f'| P90 | {p90:.1f}s |')
    report.append(f'| P99 | {p99:.1f}s |')
    report.append(f'| API成功率 | {len(success)}/{total} ({len(success)/max(total,1)*100:.1f}%) |')
    report.append('')

    return '\n'.join(report)


def main():
    if not API_KEY:
        print('错误: 请设置环境变量 DIFY_API_KEY')
        print('  export DIFY_API_KEY=app-xxxx')
        sys.exit(1)

    eval_set_path = EVAL_SET
    if not os.path.exists(eval_set_path):
        print(f'错误: 评测集文件不存在: {eval_set_path}')
        sys.exit(1)

    with open(eval_set_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)

    print(f'加载 {len(cases)} 条评测用例')

    results, total_time = asyncio.run(run_eval(cases))

    results_path = os.path.join(OUTPUT_DIR, 'eval_results.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\n详细结果: {results_path}')

    report = generate_report(results, total_time)
    report_path = os.path.join(OUTPUT_DIR, 'eval_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f'评测报告: {report_path}')

    print(f'\n{report}')


if __name__ == '__main__':
    main()
