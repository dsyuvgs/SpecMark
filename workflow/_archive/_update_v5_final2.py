import yaml
import re
import shutil

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'
BACKUP_PATH = YAML_PATH + '.v5bak6'

shutil.copy2(BACKUP_PATH, YAML_PATH, )
print(f"Restored from backup")

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    raw_text = f.read()

v5_source = open(r'd:\产品分析\SpecMark\workflow\_v5_test.py', 'r', encoding='utf-8').read()
func_start = v5_source.find('def iron_classify_v5(text):')
func_end = v5_source.find('\n\ntype_map', func_start)
v5_func_code = v5_source[func_start:func_end]
v5_func_code = v5_func_code.replace('iron_classify_v5', 'iron_classify')
v5_func_code = v5_func_code.rstrip() + '\n'

def extract_yaml_double_quoted_string(text, start_pos):
    pos = start_pos
    assert text[pos] == '"', f"Expected '\"' at position {pos}, got '{text[pos]}'"
    pos += 1
    result = []
    while pos < len(text):
        ch = text[pos]
        if ch == '\\':
            if pos + 1 < len(text):
                next_ch = text[pos + 1]
                if next_ch == '"':
                    result.append('"')
                    pos += 2
                elif next_ch == '\\':
                    result.append('\\')
                    pos += 2
                elif next_ch == 'n':
                    result.append('\n')
                    pos += 2
                elif next_ch == 't':
                    result.append('\t')
                    pos += 2
                elif next_ch == '\n':
                    pos += 2
                    while pos < len(text) and text[pos] in ' \t':
                        pos += 1
                    if pos < len(text) and text[pos] == '\\':
                        pos += 1
                else:
                    result.append(next_ch)
                    pos += 2
            else:
                result.append(ch)
                pos += 1
        elif ch == '"':
            return ''.join(result), pos + 1
        else:
            result.append(ch)
            pos += 1
    return None, pos

def code_to_yaml_with_continuation(code, indent='        ', max_len=80):
    escaped = code.replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace('\n', '\\n')
    escaped = escaped.replace('\t', '\\t')
    
    result = '"' + escaped[:max_len]
    pos = max_len
    while pos < len(escaped):
        chunk_end = min(pos + max_len, len(escaped))
        chunk = escaped[pos:chunk_end]
        result += '\\\n' + indent + '\\ ' + chunk
        pos = chunk_end
    result += '"'
    return result

# Step 1: Find all code fields with iron_classify
matches = []
for m in re.finditer(r'^(\s+)code:\s+"', raw_text, re.MULTILINE):
    indent = m.group(1)
    quote_start = m.end() - 1
    
    code_value, end_pos = extract_yaml_double_quoted_string(raw_text, quote_start)
    if code_value is None:
        print(f"WARNING: Could not extract code value at position {quote_start}")
        continue
    
    if 'iron_classify' not in code_value:
        continue
    
    matches.append({
        'quote_start': quote_start,
        'end_pos': end_pos,
        'code_value': code_value,
        'indent': indent,
    })

print(f"Found {len(matches)} code nodes with iron_classify")

# Step 2: Process each match
replacements = []
for match in matches:
    new_code = match['code_value']
    
    # 1. Replace iron_classify function
    func_start_pos = new_code.find('def iron_classify(text):')
    if func_start_pos < 0:
        continue
    
    search_from = func_start_pos + 10
    end_markers = []
    for em in re.finditer(r'\n        def \w+', new_code[search_from:]):
        end_markers.append(search_from + em.start())
        break
    for pattern in ['\n   result = iron_classify', '\n    result = iron_classify', '\n        result = iron_classify']:
        pos = new_code.find(pattern, search_from)
        if pos >= 0:
            end_markers.append(pos)
    
    if not end_markers:
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
    
    # 3. Replace priority handler for single-feedback nodes
    old_prio = re.search(
        r"priority\s*=\s*llm_result\.get\('priority',\s*'低'\)\s+if\s+prioritynot\s+in\s+\['高',\s*'中',\s*'低'\]:\s+priority\s*=\s*'低'",
        new_code
    )
    if old_prio:
        new_prio = "if iron_priority is not None:\n                priority = iron_priority\n            else:\n                priority = llm_result.get('priority', '低')\n                if priority not in ['高', '中', '低']:\n                    priority = '低'"
        new_code = new_code[:old_prio.start()] + new_prio + new_code[old_prio.end():]
        print(f"  Replaced priority handler (single-feedback)")
    else:
        batch_prio = re.search(
            r"ptype, sentiment, iron_priority = result\s+else:\s+ptype\s*=\s*'体验'\s+sentiment\s*=\s*'中性'\s+priority\s*=\s*'低'",
            new_code
        )
        if batch_prio:
            new_batch_prio = "ptype, sentiment, iron_priority = result\n            priority = iron_priority if iron_priority is not None else '低'\n        else:\n            ptype = '体验'\n            sentiment = '中性'\n            priority = '低'"
            new_code = new_code[:batch_prio.start()] + new_batch_prio + new_code[batch_prio.end():]
            print(f"  Replaced priority handler (batch)")
    
    new_yaml_value = code_to_yaml_with_continuation(new_code, indent=match['indent'] + '  ')
    replacements.append({
        'quote_start': match['quote_start'],
        'end_pos': match['end_pos'],
        'new_yaml_value': new_yaml_value,
    })

# Step 3: Apply replacements from end to start
replacements.sort(key=lambda x: x['quote_start'], reverse=True)
for r in replacements:
    raw_text = raw_text[:r['quote_start']] + r['new_yaml_value'] + raw_text[r['end_pos']:]
    print(f"Replaced code at position {r['quote_start']}")

with open(YAML_PATH, 'w', encoding='utf-8') as f:
    f.write(raw_text)

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

# Check line lengths
with open(YAML_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()
max_line = max(len(line) for line in lines)
print(f"\nLongest line: {max_line} chars")
long_lines = sum(1 for line in lines if len(line) > 200)
print(f"Lines > 200 chars: {long_lines}")

print("\nDone!")
