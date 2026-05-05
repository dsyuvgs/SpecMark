import yaml
import re
import shutil

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'
BACKUP_PATH = YAML_PATH + '.v5bak4'

shutil.copy2(YAML_PATH, BACKUP_PATH)
print(f"Backup: {BACKUP_PATH}")

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    raw_text = f.read()

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

v5_source = open(r'd:\产品分析\SpecMark\workflow\_v5_test.py', 'r', encoding='utf-8').read()
func_start = v5_source.find('def iron_classify_v5(text):')
func_end = v5_source.find('\n\ntype_map', func_start)
v5_func_code = v5_source[func_start:func_end]
v5_func_code = v5_func_code.replace('iron_classify_v5', 'iron_classify')
v5_func_code = v5_func_code.rstrip() + '\n'

def code_to_yaml_value(code):
    escaped = code.replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace('\n', '\\n')
    escaped = escaped.replace('\t', '\\t')
    return '"' + escaped + '"'

nodes = data['workflow']['graph']['nodes']
replacements_made = 0

for node in nodes:
    nd = node.get('data', {})
    if nd.get('type') != 'code' or 'code' not in nd:
        continue
    old_code = nd['code']
    if 'iron_classify' not in old_code:
        continue

    title = nd.get('title', 'unknown')
    print(f"\nProcessing: {title}")

    new_code = old_code

    # 1. Replace iron_classify function
    func_start_pos = new_code.find('def iron_classify(text):')
    if func_start_pos < 0:
        print(f"  WARNING: Could not find iron_classify")
        continue

    search_from = func_start_pos + 10
    end_markers = []
    for m in re.finditer(r'\n        def \w+', new_code[search_from:]):
        end_markers.append(search_from + m.start())
        break
    for pattern in ['\n   result = iron_classify', '\n    result = iron_classify', '\n        result = iron_classify']:
        pos = new_code.find(pattern, search_from)
        if pos >= 0:
            end_markers.append(pos)

    if not end_markers:
        print(f"  WARNING: Could not find end of iron_classify function")
        continue

    func_end_pos = min(end_markers)
    new_code = new_code[:func_start_pos] + v5_func_code + new_code[func_end_pos:]
    print(f"  Replaced iron_classify function")

    # 2. Replace result handler for single-feedback nodes
    old_handler = re.search(
        r"result\s*=\s*iron_classify\(text\)\s+if\s+result:\s+ptype,\s*sentiment\s*,\s*priority\s*=\s*result\s+source\s*=\s*'铁律拦截'",
        new_code
    )
    if old_handler:
        new_handler = "result = iron_classify(text)\n    if result:\n        ptype, sentiment, iron_priority = result\n        source = '铁律拦截'"
        new_code = new_code[:old_handler.start()] + new_handler + new_code[old_handler.end():]
        print(f"  Replaced result handler (single-feedback)")
    else:
        old_batch_handler = re.search(
            r"result\s*=\s*iron_classify\(feedback_text\)\s+if\s+result:\s+ptype,\s*sentiment,\s*priority\s*=\s*result",
            new_code
        )
        if old_batch_handler:
            new_batch_handler = "result = iron_classify(feedback_text)\n        if result:\n            ptype, sentiment, iron_priority = result"
            new_code = new_code[:old_batch_handler.start()] + new_batch_handler + new_code[old_batch_handler.end():]
            print(f"  Replaced result handler (batch)")
        else:
            print(f"  WARNING: Could not find result handler")

    # 3. Replace priority handler for single-feedback nodes
    old_prio = re.search(
        r"priority\s*=\s*llm_result\.get\('priority',\s*'低'\)\s+if\s+prioritynot\s+in\s+\['高',\s*'中',\s*'低'\]:\s+priority\s*=\s*'低'",
        new_code
    )
    if old_prio:
        new_prio = "if iron_priority is not None:\n                priority = iron_priority\n            else:\n                priority = llm_result.get('priority', '低')\n                if priority not in ['高', '中', '低']:\n                    priority = '低'"
        new_code = new_code[:old_prio.start()] + new_prio + new_code[old_prio.end():]
        print(f"  Replaced priority handler (single-feedback, also fixed 'prioritynot' bug)")
    else:
        batch_prio = re.search(
            r"ptype, sentiment, iron_priority = result\s+else:\s+ptype\s*=\s*'体验'\s+sentiment\s*=\s*'中性'\s+priority\s*=\s*'低'",
            new_code
        )
        if batch_prio:
            new_batch_prio = "ptype, sentiment, iron_priority = result\n            priority = iron_priority if iron_priority is not None else '低'\n        else:\n            ptype = '体验'\n            sentiment = '中性'\n            priority = '低'"
            new_code = new_code[:batch_prio.start()] + new_batch_prio + new_code[batch_prio.end():]
            print(f"  Replaced priority handler (batch)")
        else:
            print(f"  WARNING: Could not find priority handler")

    # Now do raw text replacement
    old_yaml_value = code_to_yaml_value(old_code)
    new_yaml_value = code_to_yaml_value(new_code)

    if old_yaml_value in raw_text:
        raw_text = raw_text.replace(old_yaml_value, new_yaml_value, 1)
        replacements_made += 1
        print(f"  Raw text replacement: SUCCESS")
    else:
        print(f"  Raw text replacement: FAILED - trying line-by-line search")
        old_lines = old_yaml_value.split('\\n')
        search_snippet = old_lines[0][:80] if old_lines else old_yaml_value[:80]
        print(f"  Looking for: {repr(search_snippet)}...")
        
        pos = raw_text.find('code: "import json')
        if pos < 0:
            pos = raw_text.find('code: "import re')
        if pos >= 0:
            print(f"  Found code: at position {pos}")
            print(f"  Context: {repr(raw_text[pos:pos+100])}")

print(f"\n\nTotal raw text replacements: {replacements_made}")

with open(YAML_PATH, 'w', encoding='utf-8') as f:
    f.write(raw_text)

print("YAML written. Validating...")

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
