import yaml
import re
import shutil
import py_compile
import tempfile
import os

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'
BACKUP_PATH = YAML_PATH + '.v5bak6'

shutil.copy2(BACKUP_PATH, YAML_PATH)
print("Restored from backup")

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
    assert text[pos] == '"'
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

def fix_code_bugs(code):
    # Fix stray 'n' before def statements (from YAML \\nn bug)
    code = code.replace('\nn    def iron_classify', '\n    def iron_classify')
    code = code.replace('\nn    def is_core_func', '\n    def is_core_func')
    
    # Fix missing spaces in keywords
    code = code.replace('prioritynot ', 'priority not ')
    code = code.replace('sentimentnot ', 'sentiment not ')
    code = code.replace('forpattern,', 'for pattern,')
    code = code.replace('returnneed', 'return need')
    
    # Fix indentation: lines with 3,7,11,15,19 spaces should be 4,8,12,16,20
    # This is caused by YAML line continuation stripping 1 char
    lines = code.split('\n')
    fixed_lines = []
    for line in lines:
        if not line.strip():
            fixed_lines.append(line)
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent in (3, 7, 11, 15, 19, 23, 27, 31):
            fixed_lines.append(' ' + line)
        else:
            fixed_lines.append(line)
    code = '\n'.join(fixed_lines)
    
    return code

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
    new_code = fix_code_bugs(old_code)
    
    # 1. Replace iron_classify function
    func_start_pos = new_code.find('def iron_classify(text):')
    if func_start_pos < 0:
        print("WARNING: Could not find iron_classify")
        continue
    
    prev_newline = new_code.rfind('\n', 0, func_start_pos)
    line_start = prev_newline + 1 if prev_newline >= 0 else 0
    existing_indent = func_start_pos - line_start
    print(f"\n  iron_classify indent: {existing_indent} spaces")
    
    search_from = func_start_pos + 10
    end_markers = []
    for em in re.finditer(r'\n    def \w+', new_code[search_from:]):
        end_markers.append(search_from + em.start())
        break
    for pattern in ['\n    result = iron_classify', '\n        result = iron_classify']:
        pos = new_code.find(pattern, search_from)
        if pos >= 0:
            end_markers.append(pos)
    
    if not end_markers:
        print("  WARNING: Could not find end of iron_classify")
        continue
    
    func_end_pos = min(end_markers)
    
    v5_lines = v5_func_code.split('\n')
    v5_indented_lines = []
    for i, line in enumerate(v5_lines):
        if line.strip():
            v5_indented_lines.append(' ' * existing_indent + line)
        else:
            v5_indented_lines.append(line)
    v5_indented = '\n'.join(v5_indented_lines)
    
    new_code = new_code[:line_start] + v5_indented + new_code[func_end_pos:]
    print(f"  Replaced iron_classify with V5 (indent={existing_indent})")
    
    # 2. Replace result handler
    is_batch = 'result = iron_classify(feedback_text)' in new_code
    
    if not is_batch:
        old_handler = re.search(
            r'([ \t]*)result = iron_classify\(text\)\n([ \t]*)if result:\n([ \t]*)ptype, sentiment,\s*iron_priority = result\n([ \t]*)source = [\'"]\xe9\x93\x81\xe5\xbe\x8b\xe6\x8b\xa6\xe6\x88\xaa[\'"]',
            new_code
        )
        if not old_handler:
            old_handler = re.search(
                r'([ \t]*)result = iron_classify\(text\)\n([ \t]*)if result:\n([ \t]*)ptype, sentiment,\s*priority = result\n([ \t]*)source = [\'"]\xe9\x93\x81\xe5\xbe\x8b\xe6\x8b\xa6\xe6\x88\xaa[\'"]',
                new_code
            )
        
        if old_handler:
            base = old_handler.group(1)
            inner = old_handler.group(2)
            inner2 = old_handler.group(3)
            inner3 = old_handler.group(4)
            
            new_handler = (
                f"{base}result = iron_classify(text)\n"
                f"{inner}if result:\n"
                f"{inner2}ptype, sentiment, iron_priority = result\n"
                f"{inner3}source = '\u94c1\u5f8b\u62e6\u622a'"
            )
            new_code = new_code[:old_handler.start()] + new_handler + new_code[old_handler.end():]
            print(f"  Replaced result handler (single-feedback)")
    else:
        old_handler = re.search(
            r'([ \t]*)result = iron_classify\(feedback_text\)\n([ \t]*)if result:\n([ \t]*)ptype, sentiment,\s*(?:iron_)?priority = result',
            new_code
        )
        if old_handler:
            base = old_handler.group(1)
            inner = old_handler.group(2)
            inner2 = old_handler.group(3)
            
            new_handler = (
                f"{base}result = iron_classify(feedback_text)\n"
                f"{inner}if result:\n"
                f"{inner2}ptype, sentiment, iron_priority = result"
            )
            new_code = new_code[:old_handler.start()] + new_handler + new_code[old_handler.end():]
            print(f"  Replaced result handler (batch)")
    
    # 3. Replace priority handler
    if not is_batch:
        old_prio = re.search(
            r"([ \t]*)priority = llm_result\.get\('priority',\s*'低'\)\n([ \t]*)if priority not in \['高',\s*'中',\s*'低'\]:\n([ \t]*)priority = '低'",
            new_code
        )
        if old_prio:
            base = old_prio.group(1)
            inner = base + '    '
            inner2 = inner + '    '
            
            new_prio = (
                f"{base}if iron_priority is not None:\n"
                f"{inner}priority = iron_priority\n"
                f"{base}else:\n"
                f"{inner}priority = llm_result.get('priority', '\u4f4e')\n"
                f"{inner}if priority not in ['\u9ad8', '\u4e2d', '\u4f4e']:\n"
                f"{inner2}priority = '\u4f4e'"
            )
            new_code = new_code[:old_prio.start()] + new_prio + new_code[old_prio.end():]
            print(f"  Replaced priority handler (single-feedback)")
        else:
            print(f"  WARNING: Could not find priority handler")
    else:
        old_batch_prio = re.search(
            r"([ \t]*)ptype, sentiment,\s*(?:iron_)?priority = result\n([ \t]*)else:\n([ \t]*)ptype = '体验'\n([ \t]*)sentiment = '中性'\n([ \t]*)priority = '低'",
            new_code
        )
        if old_batch_prio:
            base = old_batch_prio.group(1)
            inner = old_batch_prio.group(2)
            inner2 = old_batch_prio.group(3)
            inner3 = old_batch_prio.group(4)
            inner4 = old_batch_prio.group(5)
            
            new_batch_prio = (
                f"{base}ptype, sentiment, iron_priority = result\n"
                f"{inner}priority = iron_priority if iron_priority is not None else '\u4f4e'\n"
                f"{inner2}else:\n"
                f"{inner3}ptype = '\u4f53\u9a8c'\n"
                f"{inner4}sentiment = '\u4e2d\u6027'\n"
                f"{inner4}priority = '\u4f4e'"
            )
            new_code = new_code[:old_batch_prio.start()] + new_batch_prio + new_code[old_batch_prio.end():]
            print(f"  Replaced priority handler (batch)")
        else:
            print(f"  WARNING: Could not find batch priority handler")
    
    # 4. Validate
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
        debug_path = f'd:\\产品分析\\SpecMark\\workflow\\_debug_failed_v2.py'
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"  Saved to: {debug_path}")
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
    print(f"\nApplied replacement at position {r['quote_start']}")

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
                has_prioritynot = 'prioritynot' in code
                has_stray_n = '\nn    def iron_classify' in code
                
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
                
                print(f"  {title}:")
                print(f"    V5={has_none}, iron_priority={has_iron_priority}")
                print(f"    prioritynot={has_prioritynot}, stray_n={has_stray_n}")
                print(f"    compile={'OK' if compile_ok else 'FAIL'}")
except Exception as e:
    print(f"YAML validation FAILED: {e}")

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()
max_line = max(len(line) for line in lines)
print(f"\nLongest line: {max_line} chars")
print("\nDone!")
