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
        
        # Find iron_classify
        func_pos = code.find('def iron_classify(text):')
        if func_pos < 0:
            print("  iron_classify NOT FOUND")
            continue
        
        # Find line start
        prev_nl = code.rfind('\n', 0, func_pos)
        line_start = prev_nl + 1 if prev_nl >= 0 else 0
        indent = func_pos - line_start
        
        # Show exact chars before def
        before_def = code[line_start:func_pos]
        print(f"  Chars before 'def': {repr(before_def)} (len={len(before_def)})")
        print(f"  Indent: {indent} spaces")
        
        # Show first 3 body lines
        body_start = func_pos + len('def iron_classify(text):')
        body_text = code[body_start:body_start+300]
        body_lines = body_text.split('\n')
        for i, line in enumerate(body_lines[:5]):
            stripped = line.lstrip()
            indent_count = len(line) - len(stripped) if stripped else 0
            print(f"  Body line {i}: indent={indent_count} | {repr(line[:80])}")
        
        # Find result handler
        for pattern in ['result = iron_classify(text)', 'result = iron_classify(feedback_text)']:
            rpos = code.find(pattern)
            if rpos >= 0:
                rprev_nl = code.rfind('\n', 0, rpos)
                rline_start = rprev_nl + 1 if rprev_nl >= 0 else 0
                rbefore = code[rline_start:rpos]
                print(f"\n  Result handler '{pattern}':")
                print(f"    Chars before: {repr(rbefore)} (len={len(rbefore)})")
                
                # Show next 5 lines
                after = code[rpos:rpos+200]
                for i, line in enumerate(after.split('\n')[:5]):
                    stripped = line.lstrip()
                    indent_count = len(line) - len(stripped) if stripped else 0
                    print(f"    Line {i}: indent={indent_count} | {repr(line[:80])}")
                break
        
        # Find priority handler
        for pp in ['prioritynot', 'priority not', 'priority = llm_result']:
            ppos = code.find(pp)
            if ppos >= 0:
                pprev_nl = code.rfind('\n', 0, ppos)
                pline_start = pprev_nl + 1 if pprev_nl >= 0 else 0
                pbefore = code[pline_start:ppos]
                print(f"\n  Priority handler '{pp}':")
                print(f"    Chars before: {repr(pbefore)} (len={len(pbefore)})")
                
                after = code[ppos:ppos+200]
                for i, line in enumerate(after.split('\n')[:5]):
                    stripped = line.lstrip()
                    indent_count = len(line) - len(stripped) if stripped else 0
                    print(f"    Line {i}: indent={indent_count} | {repr(line[:80])}")
                break
        
        # Save full code
        out_path = f'd:\\产品分析\\SpecMark\\workflow\\_orig_{title}.py'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"\n  Saved to: {out_path}")
