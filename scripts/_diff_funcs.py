import yaml, re, hashlib

with open('workflow/SpecMark最新.yml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data.get('workflow', {}).get('graph', {}).get('nodes', [])
code_nodes = []
for n in nodes:
    nd = n.get('data', {})
    if nd.get('type') == 'code' and nd.get('code'):
        code_nodes.append({'id': n['id'], 'title': nd.get('title', '?'), 'code': nd['code']})

def extract_func(code, fname):
    """Extract function body precisely by tracking indent"""
    lines = code.split('\n')
    start = -1
    for i, line in enumerate(lines):
        if re.match(rf'def {fname}\(', line.strip()):
            start = i
            break
    if start < 0:
        return None
    
    base_indent = len(lines[start]) - len(lines[start].lstrip())
    body_lines = [lines[start]]
    for i in range(start + 1, len(lines)):
        line = lines[i]
        if line.strip() == '':
            body_lines.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= base_indent and line.strip():
            break
        body_lines.append(line)
    return '\n'.join(body_lines)

iron_nodes = [cn for cn in code_nodes if 'iron_classify' in cn['code']]
print('=== iron_classify 逐节点对比 ===')
funcs = {}
for cn in iron_nodes:
    f = extract_func(cn['code'], 'iron_classify')
    if f:
        funcs[cn['title']] = f
        print(f'\n--- [{cn["title"]}] ({cn["id"]}) ---')
        print(f'行数: {len(f.split(chr(10)))}')
        print(f'SHA256: {hashlib.sha256(f.encode()).hexdigest()[:16]}')

# Compare pairwise
titles = list(funcs.keys())
for i in range(len(titles)):
    for j in range(i+1, len(titles)):
        t1, t2 = titles[i], titles[j]
        if funcs[t1] == funcs[t2]:
            print(f'\n{t1} == {t2}: 完全一致')
        else:
            print(f'\n{t1} != {t2}: 不一致!')
            l1 = funcs[t1].split('\n')
            l2 = funcs[t2].split('\n')
            max_len = max(len(l1), len(l2))
            diffs = 0
            for k in range(max_len):
                a = l1[k] if k < len(l1) else '<缺失>'
                b = l2[k] if k < len(l2) else '<缺失>'
                if a != b:
                    diffs += 1
                    if diffs <= 10:
                        print(f'  L{k+1}:')
                        print(f'    [{t1}]: {a[:120]}')
                        print(f'    [{t2}]: {b[:120]}')
            print(f'  总差异行数: {diffs}')

print('\n=== apply_priority_rules 逐节点对比 ===')
apr_nodes = [cn for cn in code_nodes if 'apply_priority_rules' in cn['code']]
funcs2 = {}
for cn in apr_nodes:
    f = extract_func(cn['code'], 'apply_priority_rules')
    if f:
        funcs2[cn['title']] = f
        print(f'\n--- [{cn["title"]}] ---')
        print(f'行数: {len(f.split(chr(10)))}')
        print(f'SHA256: {hashlib.sha256(f.encode()).hexdigest()[:16]}')

titles2 = list(funcs2.keys())
for i in range(len(titles2)):
    for j in range(i+1, len(titles2)):
        t1, t2 = titles2[i], titles2[j]
        if funcs2[t1] == funcs2[t2]:
            print(f'\n{t1} == {t2}: 完全一致')
        else:
            print(f'\n{t1} != {t2}: 不一致!')
            l1 = funcs2[t1].split('\n')
            l2 = funcs2[t2].split('\n')
            max_len = max(len(l1), len(l2))
            diffs = 0
            for k in range(max_len):
                a = l1[k] if k < len(l1) else '<缺失>'
                b = l2[k] if k < len(l2) else '<缺失>'
                if a != b:
                    diffs += 1
                    if diffs <= 10:
                        print(f'  L{k+1}:')
                        print(f'    [{t1}]: {a[:120]}')
                        print(f'    [{t2}]: {b[:120]}')
            print(f'  总差异行数: {diffs}')
