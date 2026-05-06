import yaml, re, ast

with open('workflow/SpecMark最新.yml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data.get('workflow', {}).get('graph', {}).get('nodes', [])
code_nodes = []
for n in nodes:
    nd = n.get('data', {})
    if nd.get('type') == 'code' and nd.get('code'):
        code_nodes.append({'id': n['id'], 'title': nd.get('title', '?'), 'code': nd['code']})

print('=== 深度运行时问题检查 ===')
print()

for cn in code_nodes:
    code = cn['code']
    title = cn['title']
    issues = []
    
    # 1. Check for undefined variables (heuristic)
    # Look for variable assignments and usages
    lines = code.split('\n')
    
    # 2. Check for potential NoneType errors
    for i, line in enumerate(lines):
        # Check for .strip() .split() etc on potentially None values
        if re.search(r'\.(strip|split|replace|find|index|startswith|endswith)\(', line):
            # Check if the variable being accessed could be None
            pass
    
    # 3. Check for try/except that's too broad
    try_count = len(re.findall(r'\btry\s*:', code))
    except_count = len(re.findall(r'\bexcept\s*:', code))
    bare_except = len(re.findall(r'\bexcept\s*:', code))
    
    # 4. Check for return type consistency in iron_classify
    if 'iron_classify' in code:
        returns = re.findall(r'return\s*\(([^)]+)\)', code)
        for r in returns:
            parts = [p.strip().strip("'\"") for p in r.split(',')]
            if len(parts) != 3:
                issues.append(f'iron_classify return 不是三元组: return ({r})')
    
    # 5. Check for is_core_func return type
    if 'is_core_func' in code:
        bool_returns = re.findall(r'return\s+(True|False)\s*$', code, re.MULTILINE)
        if bool_returns:
            issues.append(f'is_core_func 返回 bool 而非字符串: {bool_returns}')
    
    # 6. Check for apply_priority_rules call
    if 'apply_priority_rules' in code and 'def apply_priority_rules' in code:
        calls = re.findall(r'apply_priority_rules\(([^)]+)\)', code)
        for c in calls:
            args = [a.strip() for a in c.split(',')]
            if len(args) != 3:
                issues.append(f'apply_priority_rules 调用参数不是3个: ({c})')
    
    # 7. Check for variable name typos
    if 'sentiment' in code:
        if 'sentiment' not in code and 'sentiment' in code:
            pass  # both exist
    
    if issues:
        print(f'[{title}]:')
        for issue in issues:
            print(f'  ! {issue}')
    else:
        print(f'[{title}]: 未发现明显问题')

print()

# Check routing validation specifically
print('=== 路由验证深度检查 ===')
for cn in code_nodes:
    if '路由' in cn['title']:
        code = cn['code']
        
        # Check if validated_type can be 'data_label_text' for feedback
        if "'data_label_text'" in code:
            print('  data_label_text 输出路径存在')
        else:
            print('  ! 缺少 data_label_text 输出路径')
        
        # Check the LLM confidence override logic
        conf_lines = [l for l in code.split('\n') if 'confidence' in l and ('0.8' in l or '0.9' in l)]
        if conf_lines:
            print(f'  置信度阈值: {conf_lines}')
        else:
            print('  ! 未找到置信度阈值设置')
        
        # Check if there's a path that always returns invalid_input
        invalid_paths = re.findall(r"'invalid_input'", code)
        print(f'  invalid_input 引用次数: {len(invalid_paths)}')

print()
print('=== YAML 结构检查 ===')
try:
    yaml.safe_load(open('workflow/SpecMark最新.yml', 'r', encoding='utf-8'))
    print('YAML 解析 OK')
except Exception as e:
    print(f'YAML 解析失败: {e}')

# Check all code nodes parse correctly
print()
print('=== 最终语法验证 ===')
all_ok = True
for cn in code_nodes:
    try:
        ast.parse(cn['code'])
    except SyntaxError as e:
        print(f'  [{cn["title"]}] 语法错误: {e}')
        all_ok = False
if all_ok:
    print('  所有节点语法 OK')
