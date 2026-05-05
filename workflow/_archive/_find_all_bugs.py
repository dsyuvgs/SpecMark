import yaml
import re

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml.v5bak6'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data['workflow']['graph']['nodes']
for node in nodes:
    nd = node.get('data', {})
    if nd.get('type') == 'code' and 'code' in nd:
        code = nd['code']
        title = nd.get('title', '?')
        if 'iron_classify' not in code:
            continue
        
        print(f"\n=== {title} ===")
        
        # Find ALL lines starting with stray 'n' followed by spaces
        lines = code.split('\n')
        for i, line in enumerate(lines):
            # Check for stray 'n' at line start: n followed by 4+ spaces
            m = re.match(r'^n(\s{4,}\S)', line)
            if m:
                print(f"  Line {i+1}: STRAY 'n' -> {repr(line[:60])}")
            
            # Check for stray 'n' at line end after string
            if line.rstrip().endswith('"n') or line.rstrip().endswith("'n"):
                print(f"  Line {i+1}: STRAY 'n' at end -> {repr(line[-20:])}")
            
            # Check for non-standard indentation (3,7,11,15,19,23,27,31)
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent in (3, 7, 11, 15, 19, 23, 27, 31):
                    print(f"  Line {i+1}: INDENT={indent} -> {repr(line[:60])}")
            
            # Check for missing spaces in keywords
            for bug in ['prioritynot', 'sentimentnot', 'forpattern', 'returnneed']:
                if bug in line:
                    print(f"  Line {i+1}: KEYWORD BUG '{bug}' -> {repr(line[:60])}")
