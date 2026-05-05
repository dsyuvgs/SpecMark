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

    title = nd.get('title', 'unknown')
    print(f"\n=== {title} ===")

    func_start_pos = code.find('def iron_classify(text):')
    print(f"Function starts at pos: {func_start_pos}")

    search_from = func_start_pos + 10

    for pattern in ['\n   result = iron_classify', '\n    result = iron_classify', '\n        result = iron_classify']:
        pos = code.find(pattern, search_from)
        print(f"  Pattern {repr(pattern[:30])}: pos={pos}")

    # Show what comes after the function
    after_func = code[func_start_pos:func_start_pos+20000]
    last_return_none = after_func.rfind('return None')
    print(f"  Last 'return None' at offset: {last_return_none}")
    print(f"  After last return None: {repr(after_func[last_return_none:last_return_none+200])}")
