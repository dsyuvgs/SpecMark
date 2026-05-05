import yaml
import re
import shutil
import py_compile
import tempfile
import os

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'
BACKUP_PATH = YAML_PATH + '.v5bak6'

shutil.copy2(BACKUP_PATH, YAML_PATH)
print(f"Restored from backup")

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

def code_to_yaml_single_line(code):
    escaped = code.replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace('\n', '\\n')
    escaped = escaped.replace('\t', '\\t')
    return '"' + escaped + '"'

def add_indent(code, spaces):
    indent_str = ' ' * spaces
    lines = code.split('\n')
    result = []
    for line in lines:
        if line.strip():
            result.append(indent_str + line)
        else:
            result.append(line)
    return '\n'.join(result)

matches = []
for m in re.finditer(r'^(\s+)code:\s+"', raw_text, re.MULTILINE):
    indent = m.group(1)
    quote_start = m.end() - 1
    code_value, end_pos = extract_yaml_double_quoted_string(raw_text, quote_start)
    if code_value is None:
        continue
    if 'iron_classify' not in code_value:
        continue
    matches.append({
        'quote_start': quote_start,
        'end_pos': end_pos,
        'code_value': code_value,
    })

print(f"Found {len(matches)} code nodes with iron_classify")

replacements = []
for match in matches:
    old_code = match['code_value']
    new_code = old_code

    # 1. Replace iron_classify function with CORRECT INDENTATION
    func_start_pos = new_code.find('def iron_classify(text):')
    if func_start_pos < 0:
        print(f"WARNING: Could not find iron_classify")
        continue

    prev_newline = new_code.rfind('\n', 0, func_start_pos)
    if prev_newline < 0:
        line_start = 0
    else:
        line_start = prev_newline + 1
    
    existing_indent = func_start_pos - line_start
    print(f"\n  iron_classify existing indent: {existing_indent} spaces")
    
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
        print(f"  WARNING: Could not find end of iron_classify function")
        continue
    
    func_end_pos = min(end_markers)
    
    v5_indented = add_indent(v5_func_code, existing_indent)
    
    new_code = new_code[:line_start] + v5_indented + new_code[func_end_pos:]
    print(f"  Replaced iron_classify function (indent={existing_indent})")

    # 2. Replace result handler - single-feedback nodes
    old_handler = re.search(
        r"result\s*=\s*iron_classify\(text\)\s+if\s+result:\s+ptype,\s*sentiment\s*,\s*priority\s*=\s*result\s+source\s*=\s*'铁律拦截'",
        new_code
    )
    if old_handler:
        handler_text = old_handler.group()
        handler_indent_match = re.search(r'(\s*)result\s*=\s*iron_classify', handler_text)
        base_indent = handler_indent_match.group(1) if handler_indent_match else '    '
        inner_indent = base_indent + '    '
        
        new_handler = (
            f"{base_indent}result = iron_classify(text)\n"
            f"{inner_indent}if result:\n"
            f"{inner_indent}    ptype, sentiment, iron_priority = result\n"
            f"{inner_indent}    source = '铁律拦截'"
        )
        new_code = new_code[:old_handler.start()] + new_handler + new_code[old_handler.end():]
        print(f"  Replaced result handler (single-feedback)")
    else:
        # Batch node
        old_batch_handler = re.search(
            r"result\s*=\s*iron_classify\(feedback_text\)\s+if\s+result:\s+ptype,\s*sentiment,\s*priority\s*=\s*result",
            new_code
        )
        if old_batch_handler:
            handler_text = old_batch_handler.group()
            handler_indent_match = re.search(r'(\s*)result\s*=\s*iron_classify', handler_text)
            base_indent = handler_indent_match.group(1) if handler_indent_match else '        '
            inner_indent = base_indent + '    '
            
            new_batch_handler = (
                f"{base_indent}result = iron_classify(feedback_text)\n"
                f"{inner_indent}if result:\n"
                f"{inner_indent}    ptype, sentiment, iron_priority = result"
            )
            new_code = new_code[:old_batch_handler.start()] + new_batch_handler + new_code[old_batch_handler.end():]
            print(f"  Replaced result handler (batch)")

    # 3. Replace priority handler - single-feedback nodes
    old_prio = re.search(
        r"priority\s*=\s*llm_result\.get\('priority',\s*'低'\)\s+if\s+prioritynot\s+in\s+\['高',\s*'中',\s*'低'\]:\s+priority\s*=\s*'低'",
        new_code
    )
    if old_prio:
        prio_text = old_prio.group()
        prio_indent_match = re.search(r'(\s*)priority\s*=\s*llm_result', prio_text)
        prio_base = prio_indent_match.group(1) if prio_indent_match else '            '
        prio_inner = prio_base + '    '
        prio_inner2 = prio_inner + '    '
        
        new_prio = (
            f"{prio_base}if iron_priority is not None:\n"
            f"{prio_inner}priority = iron_priority\n"
            f"{prio_base}else:\n"
            f"{prio_inner}priority = llm_result.get('priority', '低')\n"
            f"{prio_inner}if priority not in ['高', '中', '低']:\n"
            f"{prio_inner2}priority = '低'"
        )
        new_code = new_code[:old_prio.start()] + new_prio + new_code[old_prio.end():]
        print(f"  Replaced priority handler (single-feedback, fixed 'prioritynot' bug)")
    else:
        # Batch node
        batch_prio = re.search(
            r"ptype,\s*sentiment,\s*iron_priority\s*=\s*result\s+else:\s+ptype\s*=\s*'体验'\s+sentiment\s*=\s*'中性'\s+priority\s*=\s*'低'",
            new_code
        )
        if batch_prio:
            prio_text = batch_prio.group()
            prio_indent_match = re.search(r'(\s*)ptype', prio_text)
            prio_base = prio_indent_match.group(1) if prio_indent_match else '            '
            prio_inner = prio_base + '    '
            
            new_batch_prio = (
                f"{prio_base}ptype, sentiment, iron_priority = result\n"
                f"{prio_inner}priority = iron_priority if iron_priority is not None else '低'\n"
                f"{prio_base}else:\n"
                f"{prio_inner}ptype = '体验'\n"
                f"{prio_inner}sentiment = '中性'\n"
                f"{prio_inner}priority = '低'"
            )
            new_code = new_code[:batch_prio.start()] + new_batch_prio + new_code[batch_prio.end():]
            print(f"  Replaced priority handler (batch)")

    # 4. Validate modified code compiles
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
            tmp.write(new_code)
            tmp_path = tmp.name
        py_compile.compile(tmp_path, doraise=True)
        print(f"  Python compile: OK")
        os.unlink(tmp_path)
    except py_compile.PyCompileError as e:
        print(f"  Python compile: FAILED - {e}")
        os.unlink(tmp_path)
        # Save failed code for debugging
        debug_path = f'd:\\产品分析\\SpecMark\\workflow\\_debug_failed.py'
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"  Saved failed code to: {debug_path}")
        continue

    new_yaml_value = code_to_yaml_single_line(new_code)
    replacements.append({
        'quote_start': match['quote_start'],
        'end_pos': match['end_pos'],
        'new_yaml_value': new_yaml_value,
    })

# Apply replacements from end to start
replacements.sort(key=lambda x: x['quote_start'], reverse=True)
for r in replacements:
    raw_text = raw_text[:r['quote_start']] + r['new_yaml_value'] + raw_text[r['end_pos']:]
    print(f"\nReplaced code at position {r['quote_start']}")

with open(YAML_PATH, 'w', encoding='utf-8') as f:
    f.write(raw_text)

print("\nYAML written. Validating...")

try:
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        test_data = yaml.safe_load(f)
    print("YAML parse: OK")
    
    test_nodes = test_data['workflow']['graph']['nodes']
    for node in test_nodes:
        nd = node.get('data', {})
        if nd.get('type') == 'code' and 'code' in nd:
            code = nd['code']
            if 'iron_classify' in code:
                title = nd.get('title', '?')
                has_none = "return ('功能', '负向', None)" in code
                has_iron_priority = 'iron_priority' in code
                has_old_hardcoded = bool(re.search(r"return \('.*', '.*', '[高中]'\)", code))
                
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
                        tmp.write(code)
                        tmp_path = tmp.name
                    py_compile.compile(tmp_path, doraise=True)
                    compile_ok = True
                    os.unlink(tmp_path)
                except py_compile.PyCompileError as e:
                    compile_ok = False
                    os.unlink(tmp_path)
                
                print(f"  {title}: none_prio={has_none}, iron_priority={has_iron_priority}, old_hardcoded={has_old_hardcoded}, compile={'OK' if compile_ok else 'FAIL'}")
except Exception as e:
    print(f"YAML validation FAILED: {e}")

# Check format
with open(YAML_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()
max_line = max(len(line) for line in lines)
print(f"\nLongest line: {max_line} chars")

# Check key format
with open(YAML_PATH, 'r', encoding='utf-8') as f:
    first_line = f.readline()
print(f"First line: {repr(first_line[:50])}")
key_quoted = first_line.strip().startswith('"')
print(f"Keys quoted: {key_quoted}")

print("\nDone!")
