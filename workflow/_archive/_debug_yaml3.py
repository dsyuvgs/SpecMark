import yaml

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data['workflow']['graph']['nodes']
for i, node in enumerate(nodes):
    nd = node.get('data', {})
    if nd.get('type') == 'code' and 'code' in nd:
        code = nd['code']
        if 'iron_classify' in code:
            title = nd.get('title', 'unknown')
            print(f"\n{'='*60}")
            print(f"Node {i}: {title}")
            print(f"{'='*60}")
            
            # Find iron_classify function
            start = code.find('def iron_classify')
            if start >= 0:
                # Find the end of the function (next def or end of code)
                next_def = code.find('\ndef ', start + 1)
                next_result = code.find('\n   result', start + 1)
                if next_def > 0 and next_result > 0:
                    end = min(next_def, next_result)
                elif next_def > 0:
                    end = next_def
                elif next_result > 0:
                    end = next_result
                else:
                    end = len(code)
                func_code = code[start:end]
                print(f"\n--- iron_classify function (len={len(func_code)}) ---")
                print(func_code[:500])
                print("...")
                print(func_code[-300:])
            
            # Find result handler
            result_pos = code.find('result = iron_classify')
            if result_pos >= 0:
                handler_code = code[result_pos:result_pos+500]
                print(f"\n--- result handler ---")
                print(handler_code[:500])
            
            # Find priority handler
            prio_pos = code.find("priority = llm_result.get('priority'")
            if prio_pos >= 0:
                prio_code = code[prio_pos:prio_pos+200]
                print(f"\n--- priority handler ---")
                print(prio_code[:200])
