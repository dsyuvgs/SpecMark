import yaml
import re

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data['workflow']['graph']['nodes']
for node in nodes:
    nd = node.get('data', {})
    if nd.get('type') != 'code' or 'code' not in nd:
        continue
    code = nd['code']
    if 'iron_classify' not in code:
        continue

    title = nd.get('title', '?')
    print(f"\n{'='*60}")
    print(f"Node: {title}")
    print(f"{'='*60}")

    # Check iron_classify function
    func_start = code.find('def iron_classify(text):')
    func_end_markers = []
    search_from = func_start + 10
    for em in re.finditer(r'\n        def \w+', code[search_from:]):
        func_end_markers.append(search_from + em.start())
        break
    for pattern in ['\n   result = iron_classify', '\n    result = iron_classify', '\n        result = iron_classify']:
        pos = code.find(pattern, search_from)
        if pos >= 0:
            func_end_markers.append(pos)
    
    if func_end_markers:
        func_end = min(func_end_markers)
        func_code = code[func_start:func_end]
        # Check for None returns
        none_returns = len(re.findall(r"return \('.*?', '.*?', None\)", func_code))
        hardcoded_returns = len(re.findall(r"return \('.*?', '.*?', '[高中低]'\)", func_code))
        print(f"  iron_classify function length: {len(func_code)}")
        print(f"  Returns with None: {none_returns}")
        print(f"  Returns with hardcoded priority: {hardcoded_returns}")
        print(f"  First return: {repr(func_code[func_code.find('return'):func_code.find('return')+50])}")
    else:
        print(f"  WARNING: Could not find end of iron_classify function")

    # Check result handler
    if 'iron_priority' in code:
        print(f"  iron_priority variable: FOUND")
        # Show the context around iron_priority
        for m in re.finditer(r'iron_priority', code):
            start = max(0, m.start() - 30)
            end = min(len(code), m.end() + 50)
            print(f"    Context: ...{repr(code[start:end])}...")
    else:
        print(f"  iron_priority variable: NOT FOUND (WARNING!)")

    # Check priority handler
    if 'if iron_priority is not None' in code:
        print(f"  Priority handler (single): CORRECT")
    elif 'iron_priority if iron_priority is not None' in code:
        print(f"  Priority handler (batch): CORRECT")
    else:
        print(f"  Priority handler: NOT FOUND (WARNING!)")

    # Check for old bugs
    if 'prioritynot' in code:
        print(f"  BUG 'prioritynot': STILL PRESENT!")
    else:
        print(f"  BUG 'prioritynot': Fixed")

    # Check for old hardcoded priority in result handler
    if re.search(r'ptype,\s*sentiment\s*,\s*priority\s*=\s*result', code):
        print(f"  Old 'priority = result': STILL PRESENT!")
    else:
        print(f"  Old 'priority = result': Fixed")

    print(f"\n  Total code length: {len(code)}")
