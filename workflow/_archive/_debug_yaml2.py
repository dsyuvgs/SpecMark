import yaml
import json
import re

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

def find_code_nodes(data, path=''):
    results = []
    if isinstance(data, dict):
        if data.get('type') == 'code' and 'code' in data:
            code = data['code']
            if isinstance(code, str) and 'iron_classify' in code:
                results.append((path + '.code', data))
        for k, v in data.items():
            results.extend(find_code_nodes(v, f'{path}.{k}'))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            results.extend(find_code_nodes(v, f'{path}[{i}]'))
    return results

code_nodes = find_code_nodes(data)
print(f"Found {len(code_nodes)} code nodes with iron_classify")
for path, node in code_nodes:
    code = node['code']
    print(f"\n=== {path} ===")
    print(f"Code length: {len(code)}")
    print(f"First 300 chars:\n{code[:300]}")
    print(f"...")
    print(f"Last 200 chars:\n{code[-200:]}")
