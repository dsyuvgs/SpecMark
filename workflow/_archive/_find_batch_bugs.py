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
        if title != '批量分类':
            continue
        
        print(f"=== {title} ===")
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent in (3, 7, 11, 15, 19, 23, 27, 31):
                    print(f"  Line {i+1}: INDENT={indent} -> {repr(line[:80])}")
            
            for bug in ['prioritynot', 'sentimentnot', 'forpattern', 'returnneed']:
                if bug in line:
                    print(f"  Line {i+1}: KEYWORD BUG '{bug}' -> {repr(line[:80])}")
            
            m = re.match(r'^n(\s{4,}\S)', line)
            if m:
                print(f"  Line {i+1}: STRAY 'n' -> {repr(line[:80])}")
            
            if line.rstrip().endswith('"n') or line.rstrip().endswith("'n"):
                print(f"  Line {i+1}: STRAY 'n' at end -> {repr(line[-20:])}")
            
            broken = re.findall(r"'[a-z]{1,5}\s[a-z]{1,5}'", line)
            for b in broken:
                if b not in ["'铁律拦截'", "'invalid_input'", "'功能问题'", "'性能问题'", "'体验问题'", "'内容问题'"]:
                    print(f"  Line {i+1}: BROKEN WORD? {b} -> {repr(line[:80])}")
        
        with open(r'd:\产品分析\SpecMark\workflow\_orig_batch.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"\nSaved batch code to _orig_batch.py ({len(lines)} lines)")
