import yaml, re, ast, hashlib, json, sys

with open('workflow/SpecMark最新.yml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data.get('workflow', {}).get('graph', {}).get('nodes', [])
edges = data.get('workflow', {}).get('graph', {}).get('edges', [])

code_nodes = []
for n in nodes:
    nd = n.get('data', {})
    if nd.get('type') == 'code' and nd.get('code'):
        code_nodes.append({
            'id': n['id'],
            'title': nd.get('title', '?'),
            'code': nd['code'],
            'outputs': nd.get('outputs', {}),
            'variables': nd.get('variables', [])
        })

print(f'=== 代码节点总数: {len(code_nodes)} ===')
print()

# 1. Python syntax check
print('--- 1. Python 语法检查 ---')
all_ok = True
for cn in code_nodes:
    code = cn['code']
    try:
        ast.parse(code)
        print(f'  [{cn["title"]}] ({cn["id"]}) 语法 OK')
    except SyntaxError as e:
        print(f'  [{cn["title"]}] ({cn["id"]}) 语法错误: {e}')
        all_ok = False
print()

# 2. Check for common issues
print('--- 2. 常见问题检查 ---')
for cn in code_nodes:
    code = cn['code']
    title = cn['title']
    
    # Check for function defined inside another function after return
    lines = code.split('\n')
    in_func = False
    func_indent = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'def \w+\(', stripped):
            indent = len(line) - len(line.lstrip())
            if in_func and indent <= func_indent:
                pass  # new top-level function
            elif in_func and indent > func_indent:
                print(f'  [{title}] 嵌套函数定义 L{i+1}: {stripped[:60]}')
            in_func = True
            func_indent = indent
    
    # Check for return before function end
    func_lines = []
    current_func = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        m = re.match(r'def (\w+)\(', stripped)
        if m:
            current_func = m.group(1)
            func_lines = [(i, line)]
        elif current_func:
            func_lines.append((i, line))
            if stripped.startswith('return ') and i < len(lines) - 1:
                # Check if there's code after return at same indent level
                ret_indent = len(line) - len(line.lstrip())
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith('#'):
                        next_indent = len(lines[j]) - len(lines[j].lstrip())
                        if next_indent <= ret_indent and next_indent > 0:
                            if next_line.startswith('def '):
                                print(f'  [{title}] {current_func} return 后有函数定义 L{j+1}: {next_line[:60]}')
                            break

print()

# 3. Check iron_classify consistency across 3 nodes
print('--- 3. iron_classify 三节点一致性 ---')
iron_nodes = [cn for cn in code_nodes if 'iron_classify' in cn['code']]
print(f'  包含 iron_classify 的节点: {len(iron_nodes)}')

if len(iron_nodes) >= 2:
    hashes = {}
    for cn in iron_nodes:
        # Extract iron_classify function body
        m = re.search(r'def iron_classify\(.*?\n(.*?)(?=\ndef |\nclass |\Z)', cn['code'], re.DOTALL)
        if m:
            body = m.group(1)
            h = hashlib.sha256(body.encode()).hexdigest()[:12]
            hashes[cn['title']] = h
            print(f'  [{cn["title"]}] iron_classify hash: {h}')
    
    unique = set(hashes.values())
    if len(unique) == 1:
        print('  => 三个节点 iron_classify 一致')
    else:
        print(f'  => 不一致! 有 {len(unique)} 个不同版本')
        for title, h in hashes.items():
            print(f'     {title}: {h}')

print()

# 4. Check apply_priority_rules consistency
print('--- 4. apply_priority_rules 一致性 ---')
apr_nodes = [cn for cn in code_nodes if 'apply_priority_rules' in cn['code']]
print(f'  包含 apply_priority_rules 的节点: {len(apr_nodes)}')

if len(apr_nodes) >= 2:
    hashes = {}
    for cn in apr_nodes:
        m = re.search(r'def apply_priority_rules\(.*?\n(.*?)(?=\ndef |\nclass |\Z)', cn['code'], re.DOTALL)
        if m:
            body = m.group(1)
            h = hashlib.sha256(body.encode()).hexdigest()[:12]
            hashes[cn['title']] = h
            print(f'  [{cn["title"]}] apply_priority_rules hash: {h}')
    
    unique = set(hashes.values())
    if len(unique) == 1:
        print('  => 一致')
    else:
        print(f'  => 不一致! 有 {len(unique)} 个不同版本')

print()

# 5. Check output variable definitions
print('--- 5. 输出变量定义检查 ---')
for cn in code_nodes:
    outputs = cn.get('outputs', {})
    if outputs:
        print(f'  [{cn["title"]}] outputs: {list(outputs.keys())}')
    else:
        print(f'  [{cn["title"]}] 无输出定义')

print()

# 6. Check variable references across nodes
print('--- 6. 变量引用检查 ---')
# Build a map of node_id -> title
node_map = {n['id']: n.get('data', {}).get('title', '?') for n in nodes}

# Check edges for variable references
for edge in edges:
    src = edge.get('source', '')
    tgt = edge.get('target', '')
    src_handle = edge.get('sourceHandle', '')
    src_title = node_map.get(src, src)
    tgt_title = node_map.get(tgt, tgt)
    # Just list connections
    pass

# 7. Check for is_core_func type issue
print('--- 7. is_core_func 返回值检查 ---')
for cn in code_nodes:
    code = cn['code']
    if 'is_core_func' in code:
        # Check return type
        returns = re.findall(r'return\s+(True|False|\'[^\']*\'|"[^"]*")', code)
        bool_returns = [r for r in returns if r in ('True', 'False')]
        str_returns = [r for r in returns if r not in ('True', 'False')]
        if bool_returns:
            print(f'  [{cn["title"]}] is_core_func 返回 bool: {bool_returns} - 需要改为字符串!')
        elif str_returns:
            print(f'  [{cn["title"]}] is_core_func 返回 str: {str_returns} - OK')
        else:
            print(f'  [{cn["title"]}] is_core_func 返回类型不确定')

print()

# 8. Check routing validation logic
print('--- 8. 路由验证逻辑检查 ---')
for cn in code_nodes:
    if cn['title'] == '路由验证' or '路由' in cn['title']:
        code = cn['code']
        # Check if LLM confidence is used
        if 'confidence' in code:
            print(f'  [{cn["title"]}] 使用了 confidence 变量')
        else:
            print(f'  [{cn["title"]}] 未使用 confidence 变量 - 可能忽略LLM结果')
        
        # Check fallback logic
        if 'llm_type' in code:
            print(f'  [{cn["title"]}] 使用了 llm_type 变量')
        else:
            print(f'  [{cn["title"]}] 未使用 llm_type 变量')
        
        # Check for the specific fix we made
        if 'confidence >= 0.8' in code:
            print(f'  [{cn["title"]}] 已包含高置信度LLM优先逻辑')
        else:
            print(f'  [{cn["title"]}] 缺少高置信度LLM优先逻辑')

print()
print('=== 审计完成 ===')
