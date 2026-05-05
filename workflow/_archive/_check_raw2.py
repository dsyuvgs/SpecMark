YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml.v5bak6'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    raw = f.read()

# Find the first code: " with iron_classify
import re
for m in re.finditer(r'code:\s+"', raw):
    start = m.end() - 1
    # Find iron_classify in the next 50000 chars
    segment = raw[start:start+50000]
    func_pos = segment.find('iron_classify')
    if func_pos < 0:
        continue
    
    # Show 200 chars before iron_classify in raw file
    abs_pos = start + func_pos
    before = raw[abs_pos-200:abs_pos]
    after = raw[abs_pos:abs_pos+100]
    
    print("=== Raw YAML around first iron_classify ===")
    print(f"Position: {abs_pos}")
    print(f"\n--- 200 chars BEFORE ---")
    # Show with visible line breaks
    for i, line in enumerate(before.split('\n')):
        print(f"  {i}: {repr(line)}")
    print(f"\n--- AT iron_classify ---")
    for i, line in enumerate(after.split('\n')[:5]):
        print(f"  {i}: {repr(line)}")
    break

# Also check: what does yaml.safe_load produce for this code?
import yaml
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
        
        # Find iron_classify and show exact chars
        func_pos = code.find('def iron_classify(text):')
        if func_pos < 0:
            continue
        
        # Show 50 chars before
        before = code[max(0,func_pos-50):func_pos]
        print(f"\n=== {title}: parsed code around iron_classify ===")
        print(f"  Before: {repr(before)}")
        print(f"  At: {repr(code[func_pos:func_pos+50])}")
        
        # Check: is the 'n' before the spaces actually a newline?
        for i, ch in enumerate(before):
            if ch == '\n':
                print(f"  Newline at offset {i} in 'before'")
            elif ord(ch) < 32:
                print(f"  Control char {ord(ch)} at offset {i}")
