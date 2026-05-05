import yaml
import re
import shutil

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'
BACKUP_PATH = YAML_PATH + '.v5bak2'

shutil.copy2(YAML_PATH, BACKUP_PATH)
print(f"Backup: {BACKUP_PATH}")

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    raw_text = f.read()

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data['workflow']['graph']['nodes']
code_changes = {}

for node in nodes:
    nd = node.get('data', {})
    if nd.get('type') != 'code' or 'code' not in nd:
        continue
    code = nd['code']
    if 'iron_classify' not in code:
        continue

    title = nd.get('title', 'unknown')
    node_id = node.get('id', 'unknown')
    print(f"\nProcessing: {title} (id={node_id})")

    original_code = code

    # 1. Replace iron_classify function
    old_func_match = re.search(r'def iron_classify\(text\):.*?return None\n', code, re.DOTALL)
    if not old_func_match:
        old_func_match = re.search(r'def iron_classify\(text\):.*?return None$', code, re.DOTALL)
    if old_func_match:
        new_func = make_iron_classify_v5()
        code = code[:old_func_match.start()] + new_func + code[old_func_match.end():]
        print(f"  Replaced iron_classify function")
    else:
        print(f"  WARNING: Could not find iron_classify function")
        continue

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
        print(f"  Replaced priority handler (single-feedback)")
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

    code_changes[node_id] = (original_code, code)
    print(f"  Code length: {len(original_code)} -> {len(code)}")

print(f"\n\nNow doing raw text replacement...")

def code_to_yaml_quoted(code):
    escaped = code.replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace('\n', '\\n')
    escaped = escaped.replace('\t', '\\t')
    return escaped

for node_id, (old_code, new_code) in code_changes.items():
    old_yaml = code_to_yaml_quoted(old_code)
    new_yaml = code_to_yaml_quoted(new_code)

    if old_yaml in raw_text:
        raw_text = raw_text.replace(old_yaml, new_yaml, 1)
        print(f"  Node {node_id}: replaced in raw text")
    else:
        print(f"  Node {node_id}: WARNING - could not find old code in raw text!")
        print(f"  Old code first 100: {repr(old_yaml[:100])}")
        # Try to find partial match
        for start_len in range(100, 0, -10):
            partial = old_yaml[:start_len]
            if partial in raw_text:
                print(f"  Found partial match at len {start_len}")
                break

with open(YAML_PATH, 'w', encoding='utf-8') as f:
    f.write(raw_text)

print("\nValidating YAML...")
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
                has_old_prio = "'高')" in code or "'中')" in code
                print(f"  {nd.get('title', '?')}: none_prio={has_none}, iron_priority={has_iron_priority}, old_hardcoded={has_old_prio}")
except Exception as e:
    print(f"YAML validation FAILED: {e}")

print("\nDone!")
