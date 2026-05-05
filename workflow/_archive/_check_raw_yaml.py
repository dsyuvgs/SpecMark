import re

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml.v5bak6'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    raw = f.read()

# Find all code: " patterns
for m in re.finditer(r'^(\s+)code:\s+"', raw, re.MULTILINE):
    indent = m.group(1)
    quote_start = m.end() - 1
    
    # Find the end of the double-quoted string
    pos = quote_start + 1
    while pos < len(raw):
        if raw[pos] == '\\':
            pos += 2
            continue
        if raw[pos] == '"':
            break
        pos += 1
    
    code_raw = raw[quote_start:pos+1]
    
    # Check if this code contains iron_classify
    if 'iron_classify' not in code_raw:
        continue
    
    # Find iron_classify in the raw code string
    func_pos = code_raw.find('iron_classify')
    if func_pos < 0:
        continue
    
    # Show 100 chars before iron_classify
    start = max(0, func_pos - 100)
    before = code_raw[start:func_pos]
    print(f"\n=== Code node (indent={len(indent)}) ===")
    print(f"  100 chars before 'iron_classify':")
    print(f"  {repr(before)}")
    
    # Show 50 chars after iron_classify
    after = code_raw[func_pos:func_pos+50]
    print(f"  50 chars after 'iron_classify':")
    print(f"  {repr(after)}")
    
    # Check for line continuation patterns near iron_classify
    # Look for \ at end of line followed by continuation
    for i in range(max(0, func_pos-200), min(len(code_raw), func_pos+200)):
        if code_raw[i] == '\\' and i+1 < len(code_raw) and code_raw[i+1] == '\n':
            print(f"  Line continuation at pos {i}: ...{repr(code_raw[max(0,i-20):i+30])}...")
    
    # Check for '厉 害了' or 'co mment' type breakages
    for broken in ['厉 害了', 'co mment', 'te xt', 'pri ority']:
        if broken in code_raw:
            bpos = code_raw.find(broken)
            print(f"  BROKEN WORD '{broken}' at pos {bpos}: {repr(code_raw[max(0,bpos-20):bpos+30])}")
