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
    
    print(f"\n{'='*60}")
    print(f"Node: {title}")
    print(f"{'='*60}")
    
    # Find iron_classify and show surrounding code
    func_pos = code.find('def iron_classify(text):')
    start = max(0, func_pos - 100)
    end = min(len(code), func_pos + 500)
    
    print(f"--- Code around iron_classify (pos {func_pos}) ---")
    snippet = code[start:end]
    for i, line in enumerate(snippet.split('\n')):
        indent = len(line) - len(line.lstrip()) if line.strip() else 0
        print(f"  [{indent:2d}] {repr(line[:80])}")
    
    # Show the end of the function
    result_pos = code.find('result = iron_classify', func_pos)
    if result_pos < 0:
        result_pos = code.find('result = iron_classify(feedback_text)', func_pos)
    
    if result_pos > 0:
        end_snippet = code[result_pos-200:result_pos+200]
        print(f"\n--- Code around result handler ---")
        for i, line in enumerate(end_snippet.split('\n')):
            indent = len(line) - len(line.lstrip()) if line.strip() else 0
            print(f"  [{indent:2d}] {repr(line[:80])}")
    
    # Show priority handler
    prio_pos = code.find("priority = llm_result.get('priority'")
    if prio_pos < 0:
        prio_pos = code.find("priority = '低'")
    
    if prio_pos > 0:
        prio_snippet = code[prio_pos-100:prio_pos+200]
        print(f"\n--- Code around priority handler ---")
        for i, line in enumerate(prio_snippet.split('\n')):
            indent = len(line) - len(line.lstrip()) if line.strip() else 0
            print(f"  [{indent:2d}] {repr(line[:80])}")
