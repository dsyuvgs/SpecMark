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
    print(f"\n=== {title} ===")
    
    # Find all return statements with hardcoded priority
    for m in re.finditer(r"return \('.*?', '.*?', '[高中低]'\)", code):
        start = max(0, m.start() - 80)
        end = min(len(code), m.end() + 20)
        print(f"  Hardcoded: {repr(code[start:end])}")
