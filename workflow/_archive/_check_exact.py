import yaml
import re

BACKUP_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml.v5bak6'

with open(BACKUP_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data['workflow']['graph']['nodes']
for node in nodes:
    nd = node.get('data', {})
    if nd.get('type') != 'code' or 'code' not in nd:
        continue
    code = nd['code']
    title = nd.get('title', '?')
    if 'iron_classify' not in code:
        continue
    
    print(f"\n=== {title} ===")
    
    # Show exact characters around def iron_classify
    func_pos = code.find('def iron_classify(text):')
    start = max(0, func_pos - 30)
    end = min(len(code), func_pos + 30)
    print(f"Around def iron_classify: {repr(code[start:end])}")
    
    # Show the first line of the function body
    body_start = func_pos + len('def iron_classify(text):')
    body_end = min(len(code), body_start + 200)
    body_lines = code[body_start:body_end].split('\n')
    for i, line in enumerate(body_lines[:5]):
        print(f"  Body line {i}: indent={len(line) - len(line.lstrip()) if line.strip() else 'empty'} | {repr(line[:70])}")
    
    # Show result handler
    result_pos = code.find('result = iron_classify', func_pos)
    if result_pos >= 0:
        r_start = max(0, result_pos - 5)
        r_end = min(len(code), result_pos + 150)
        print(f"\nResult handler: {repr(code[r_start:r_end])}")
    
    # Show priority handler
    for pattern in ["priority = llm_result.get", "prioritynot", "ptype, sentiment, priority = result"]:
        pos = code.find(pattern, func_pos)
        if pos >= 0:
            p_start = max(0, pos - 20)
            p_end = min(len(code), pos + 100)
            print(f"Priority ({pattern[:20]}): {repr(code[p_start:p_end])}")
            break
    
    # Save full code to file for inspection
    out_path = f'd:\\产品分析\\SpecMark\\workflow\\_original_{title}.py'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"\nSaved to: {out_path}")
