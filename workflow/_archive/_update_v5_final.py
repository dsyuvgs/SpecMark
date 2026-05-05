import yaml
import re
import shutil

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'
BACKUP_PATH = YAML_PATH + '.v5bak3'

shutil.copy2(YAML_PATH, BACKUP_PATH)
print(f"Backup: {BACKUP_PATH}")

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

v5_source = open(r'd:\产品分析\SpecMark\workflow\_v5_test.py', 'r', encoding='utf-8').read()
func_start = v5_source.find('def iron_classify_v5(text):')
func_end = v5_source.find('\n\ntype_map', func_start)
v5_func_code = v5_source[func_start:func_end]
v5_func_code = v5_func_code.replace('iron_classify_v5', 'iron_classify')
v5_func_code = v5_func_code.rstrip() + '\n'

print(f"V5 function length: {len(v5_func_code)}")

nodes = data['workflow']['graph']['nodes']
modified = 0

for node in nodes:
    nd = node.get('data', {})
    if nd.get('type') != 'code' or 'code' not in nd:
        continue
    code = nd['code']
    if 'iron_classify' not in code:
        continue

    title = nd.get('title', 'unknown')
    print(f"\nProcessing: {title}")

    # 1. Find and replace iron_classify function
    func_start_pos = code.find('def iron_classify(text):')
    if func_start_pos < 0:
        print(f"  WARNING: Could not find 'def iron_classify(text):'")
        continue

    search_from = func_start_pos + 10

    # Find the end of the function by looking for the next def or result handler
    # at the same or lower indentation level
    end_markers = []

    # Look for next "def " at same level (8-space indent inside main)
    for m in re.finditer(r'\n        def \w+', code[search_from:]):
        end_markers.append(search_from + m.start())
        break

    # Look for result handler patterns
    for pattern in ['\n   result = iron_classify', '\n    result = iron_classify', '\n        result = iron_classify']:
        pos = code.find(pattern, search_from)
        if pos >= 0:
            end_markers.append(pos)

    if not end_markers:
        print(f"  WARNING: Could not find end of iron_classify function")
        continue

    func_end_pos = min(end_markers)
    old_func = code[func_start_pos:func_end_pos]
    print(f"  Old function length: {len(old_func)}")

    code = code[:func_start_pos] + v5_func_code + code[func_end_pos:]
    print(f"  Replaced iron_classify function")

    # 2. Replace result handler for single-feedback nodes
    old_handler = re.search(
        r"result\s*=\s*iron_classify\(text\)\s+if\s+result:\s+ptype,\s*sentiment\s*,\s*priority\s*=\s*result\s+source\s*=\s*'铁律拦截'",
        code
    )
    if old_handler:
        new_handler = "result = iron_classify(text)\n    if result:\n        ptype, sentiment, iron_priority = result\n        source = '铁律拦截'"
        code = code[:old_handler.start()] + new_handler + code[old_handler.end():]
        print(f"  Replaced result handler (single-feedback)")
    else:
        old_batch_handler = re.search(
            r"result\s*=\s*iron_classify\(feedback_text\)\s+if\s+result:\s+ptype,\s*sentiment,\s*priority\s*=\s*result",
            code
        )
        if old_batch_handler:
            new_batch_handler = "result = iron_classify(feedback_text)\n        if result:\n            ptype, sentiment, iron_priority = result"
            code = code[:old_batch_handler.start()] + new_batch_handler + code[old_batch_handler.end():]
            print(f"  Replaced result handler (batch)")
        else:
            print(f"  WARNING: Could not find result handler")

    # 3. Replace priority handler for single-feedback nodes
    old_prio = re.search(
        r"priority\s*=\s*llm_result\.get\('priority',\s*'低'\)\s+if\s+prioritynot\s+in\s+\['高',\s*'中',\s*'低'\]:\s+priority\s*=\s*'低'",
        code
    )
    if old_prio:
        new_prio = "if iron_priority is not None:\n                priority = iron_priority\n            else:\n                priority = llm_result.get('priority', '低')\n                if priority not in ['高', '中', '低']:\n                    priority = '低'"
        code = code[:old_prio.start()] + new_prio + code[old_prio.end():]
        print(f"  Replaced priority handler (single-feedback, also fixed 'prioritynot' bug)")
    else:
        batch_prio = re.search(
            r"ptype, sentiment, iron_priority = result\s+else:\s+ptype\s*=\s*'体验'\s+sentiment\s*=\s*'中性'\s+priority\s*=\s*'低'",
            code
        )
        if batch_prio:
            new_batch_prio = "ptype, sentiment, iron_priority = result\n            priority = iron_priority if iron_priority is not None else '低'\n        else:\n            ptype = '体验'\n            sentiment = '中性'\n            priority = '低'"
            code = code[:batch_prio.start()] + new_batch_prio + code[batch_prio.end():]
            print(f"  Replaced priority handler (batch)")
        else:
            print(f"  WARNING: Could not find priority handler")

    nd['code'] = code
    modified += 1

print(f"\n\nModified {modified} code nodes")

class DifyStringDumper(yaml.Dumper):
    pass

def str_representer(dumper, data):
    if '\n' in data or '"' in data or "'" in data or ':' in data or '#' in data:
        escaped = data.replace('\\', '\\\\')
        escaped = escaped.replace('"', '\\"')
        escaped = escaped.replace('\n', '\\n')
        escaped = escaped.replace('\t', '\\t')
        return dumper.represent_scalar('tag:yaml.org,2002:str', escaped, style='"')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

DifyStringDumper.add_representer(str, str_representer)

with open(YAML_PATH, 'w', encoding='utf-8') as f:
    yaml.dump(data, f, Dumper=DifyStringDumper, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("\nYAML written. Validating...")

try:
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        test_data = yaml.safe_load(f)
    print("YAML is valid!")

    test_nodes = test_data['workflow']['graph']['nodes']
    for node in test_nodes:
        nd = node.get('data', {})
        if nd.get('type') == 'code' and 'code' in nd:
            code = nd['code']
            if 'iron_classify' in code:
                has_none = "return ('功能', '负向', None)" in code
                has_iron_priority = 'iron_priority' in code
                has_old_hardcoded = bool(re.search(r"return \('.*', '.*', '[高中]'\)", code))
                print(f"  {nd.get('title', '?')}: none_prio={has_none}, iron_priority={has_iron_priority}, old_hardcoded={has_old_hardcoded}")
except Exception as e:
    print(f"YAML validation FAILED: {e}")

print("\nDone!")
