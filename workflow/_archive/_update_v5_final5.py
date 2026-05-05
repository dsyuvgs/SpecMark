import yaml
import re
import shutil
import py_compile
import tempfile
import os

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'
BACKUP_PATH = YAML_PATH + '.v5bak6'

shutil.copy2(BACKUP_PATH, YAML_PATH)
print("Step 1: Restored from backup")

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

def fix_all_bugs(code):
    # 1. Fix stray 'n' at line start
    lines = code.split('\n')
    fixed_lines = []
    for line in lines:
        m = re.match(r'^n(\s{4,}(?:def|return|if|for|while|try|except|with|class|assert|pass|break|continue|raise|results|else|elif))', line)
        if m:
            fixed_lines.append(line[1:])
        else:
            fixed_lines.append(line)
    code = '\n'.join(fixed_lines)
    
    # 2. Fix stray 'n' at line end after closing quote/brace
    code = re.sub(r'\}("|\')n\n', r'}\1\n', code)
    code = re.sub(r'\}("|\')n$', r'}\1', code)
    
    # 3. Fix missing spaces - known broken words from YAML line continuation
    known_fixes = [
        ('prioritynot ', 'priority not '),
        ('sentimentnot ', 'sentiment not '),
        ('forpattern,', 'for pattern,'),
        ('returnneed', 'return need'),
        ('textor ', 'text or '),
        ('textand ', 'text and '),
        ('textin ', 'text in '),
        ('textnot ', 'text not '),
        ('ifre.search', 'if re.search'),
        ('ifre.match', 'if re.match'),
        ('ifre.findall', 'if re.findall'),
        ('forre.search', 'for re.search'),
        ('forre.match', 'for re.match'),
        ('forre.findall', 'for re.findall'),
        ('returnre.search', 'return re.search'),
        ('returnre.match', 'return re.match'),
        ('returnre.findall', 'return re.findall'),
        ('notre.search', 'not re.search'),
        ('notre.match', 'not re.match'),
        ('andnot ', 'and not '),
        ('ornot ', 'or not '),
        ('ifnot ', 'if not '),
        ('fornot ', 'for not '),
        ('whilenot ', 'while not '),
        ('isnot ', 'is not '),
        ('notin ', 'not in '),
        ('notany', 'not any'),
        ('notall', 'not all'),
        ('orelse', 'or else'),
        ('andelse', 'and else'),
        ('ifany', 'if any'),
        ('ifall', 'if all'),
        ('returnany', 'return any'),
        ('returnall', 'return all'),
        ('returnnot', 'return not'),
        ('returnTrue', 'return True'),
        ('returnFalse', 'return False'),
        ('returnNone', 'return None'),
        ('=None', '= None'),
        ('=True', '= True'),
        ('=False', '= False'),
    ]
    for old, new in known_fixes:
        code = code.replace(old, new)
    
    # 4. Fix indentation: 3,7,11,15,19,23,27,31 → 4,8,12,16,20,24,28,32
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

def try_compile(code):
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        py_compile.compile(tmp_path, doraise=True)
        os.unlink(tmp_path)
        return True, None
    except py_compile.PyCompileError as e:
        os.unlink(tmp_path)
        return False, str(e)

def iterative_fix_broken_words(code, max_iterations=20):
    for iteration in range(max_iterations):
        ok, err = try_compile(code)
        if ok:
            print(f"  Iterative fix: compiled OK after {iteration} iterations")
            return code
        
        err_match = re.search(r'line (\d+)', err)
        if not err_match:
            print(f"  Iterative fix: cannot parse error line from: {err}")
            break
        
        err_line = int(err_match.group(1))
        lines = code.split('\n')
        if err_line < 1 or err_line > len(lines):
            print(f"  Iterative fix: line {err_line} out of range")
            break
        
        problem_line = lines[err_line - 1]
        
        # Try to find and fix broken words in the problem line
        fixed = False
        
        # Pattern: word merged with Python keyword
        # e.g., "ifre.search" → "if re.search"
        # e.g., "textor" → "text or"
        python_keywords = ['and', 'or', 'not', 'in', 'is', 'if', 'for', 'while', 'with', 'as',
                          'def', 'class', 'return', 'import', 'from', 'try', 'except', 'raise',
                          'pass', 'break', 'continue', 'else', 'elif', 'True', 'False', 'None',
                          'any', 'all', 'len', 'str', 'int', 'float', 'list', 'dict', 'set',
                          'tuple', 'bool', 'type', 'print', 'range', 'enumerate', 'zip', 'map',
                          'filter', 'sorted', 'reversed', 'isinstance', 'hasattr', 'getattr',
                          'setattr', 'callable', 'super', 'property', 'staticmethod', 'classmethod']
        
        for kw in python_keywords:
            # Check if keyword is merged with preceding word
            pattern = re.compile(r'(\w{2,})' + kw + r'\b')
            for m in pattern.finditer(problem_line):
                full_match = m.group(0)
                prefix = m.group(1)
                # Skip if the full match is a valid compound word
                valid_compounds = ['iron', 'login', 'margin', 'begin', 'within', 'without',
                                  'cannot', 'main', 'chain', 'obtain', 'sustain', 'refrain',
                                  'certain', 'contain', 'maintain', 'ascertain', 'determine',
                                  'examine', 'domain', 'remain', 'explain', 'complain', 'refine',
                                  'define', 'confine', 'decline', 'combine', 'assign', 'design',
                                  'resign', 'consign', 'align', 'signal', 'origin', 'imagine',
                                  'doctrine', 'routine', 'opinion', 'impose', 'expose', 'dispose',
                                  'compose', 'propose', 'suppose', 'oppose', 'purpose', 'impulse',
                                  'reconcile', 'principle', 'discipline', 'multiple', 'string',
                                  'mapping', 'mappings', 'manner', 'matter', 'pattern', 'patterns',
                                  'return', 'concern', 'confirm', 'inform', 'perform', 'transform',
                                  'platform', 'format', 'formatter', 'statement', 'requirement',
                                  'alignment', 'assignment', 'environment', 'argument', 'document',
                                  'implementation', 'component', 'consistent', 'independent',
                                  'corresponding', 'appropriate', 'approximate', 'authenticate',
                                  'authorize', 'automatic', 'available', 'applicable', 'acceptable',
                                  'accessible', 'accomplish', 'acknowledge', 'acquire', 'administer',
                                  'advocate', 'affiliate', 'aggregate', 'alleviate', 'allocate',
                                  'alternative', 'ambassador', 'annotate', 'anticipate', 'appreciate',
                                  'articulate', 'assassinate', 'assimilate', 'associate', 'attribute',
                                  'beneficiate', 'calculate', 'candidate', 'celebrate', 'certificate',
                                  'champion', 'collaborate', 'commemorate', 'communicate', 'companion',
                                  'compensate', 'concentrate', 'confiscate', 'congratulate', 'conjugate',
                                  'consecrate', 'contaminate', 'cooperate', 'corporate', 'deactivate',
                                  'degenerate', 'deliberate', 'delineate', 'demarcate', 'designate',
                                  'deteriorate', 'eliminate', 'exaggerate', 'evaluate', 'fabricate',
                                  'fascinate', 'formulate', 'frustrate', 'generate', 'gravitate',
                                  'illuminate', 'illustrate', 'imitate', 'inaugurate', 'incorporate',
                                  'indicate', 'infuriate', 'innovate', 'insinuate', 'insulate',
                                  'integrate', 'intermediate', 'interrogate', 'intimate', 'invalidate',
                                  'investigate', 'legitimate', 'liberate', 'manipulate', 'marinate',
                                  'mate', 'narrate', 'negate', 'nominate', 'obfuscate', 'obligate',
                                  'orate', 'originate', 'permeate', 'perpetuate', 'pollinate',
                                  'postulate', 'predominate', 'procrastinate', 'promulgate', 'radiate',
                                  'reactivate', 'reinstate', 'replicate', 'resonate', 'rotate',
                                  'ruminate', 'separate', 'simulate', 'stagnate', 'stimulate',
                                  'terminate', 'tolerate', 'translate', 'ultimate', 'validate',
                                  'venerate', 'vibrate', 'vindicate', 'violat', 'mandate',
                                  'reverberate', 'saturate', 'sophisticate', 'tabulate', 'undulate',
                                  'accentuate', 'adjudicate', 'alienate', 'alleviate', 'ameliorate',
                                  'annihilate', 'appropriate', 'arbitrate', 'castigate', 'commiserate',
                                  'complicate', 'confiscate', 'constipate', 'contaminate', 'corroborate',
                                  'deprecate', 'emancipate', 'expropriate', 'extrapolate', 'interpolate',
                                  'liquidate', 'macerate', 'misappropriate', 'mutilate', 'perpetrate',
                                  'punctuate', 'recriminate', 'reverberate', 'subordinate', 'understate',
                                  'overstate', 'understand', 'overstand', 'withdraw', 'withhold',
                                  'background', 'underground', 'overground', 'breakthrough',
                                  'outstanding', 'understanding', 'withstand']
                if full_match in valid_compounds:
                    continue
                if prefix in valid_compounds:
                    continue
                
                # Check if inserting a space before the keyword makes syntactic sense
                new_line = problem_line[:m.start()] + prefix + ' ' + kw + problem_line[m.end():]
                # Quick sanity: does the new line look more like valid Python?
                if re.search(r'\b(if|for|while|return|not|and|or|in|is|as|def|class)\s+' + kw, new_line):
                    lines[err_line - 1] = new_line
                    code = '\n'.join(lines)
                    print(f"  Iter {iteration}: Fixed '{full_match}' → '{prefix} {kw}' at line {err_line}")
                    fixed = True
                    break
        
        if not fixed:
            # Try another approach: look for missing space before common patterns
            # e.g., "ifre." → "if re."
            for pattern_str, replacement in [
                (r'(\w)(re\.)', r'\1 \2'),
                (r'(\w)(json\.)', r'\1 \2'),
                (r'(\w)(csv\.)', r'\1 \2'),
                (r'(\w)(os\.)', r'\1 \2'),
                (r'(\w)(sys\.)', r'\1 \2'),
            ]:
                new_line = re.sub(pattern_str, replacement, problem_line)
                if new_line != problem_line:
                    lines[err_line - 1] = new_line
                    code = '\n'.join(lines)
                    print(f"  Iter {iteration}: Fixed pattern '{pattern_str}' at line {err_line}")
                    fixed = True
                    break
        
        if not fixed:
            print(f"  Iter {iteration}: CANNOT FIX line {err_line}: {repr(problem_line[:100])}")
            # Show context
            start = max(0, err_line - 3)
            end = min(len(lines), err_line + 2)
            for i in range(start, end):
                marker = ">>>" if i == err_line - 1 else "   "
                print(f"    {marker} {i+1}: {repr(lines[i][:120])}")
            break
    
    return code

def find_iron_classify_bounds(code):
    func_start_pos = code.find('def iron_classify(text):')
    if func_start_pos < 0:
        return None, None, None
    
    prev_newline = code.rfind('\n', 0, func_start_pos)
    line_start = prev_newline + 1 if prev_newline >= 0 else 0
    existing_indent = func_start_pos - line_start
    
    search_from = func_start_pos + 10
    end_markers = []
    
    for em in re.finditer(r'\n' + ' ' * existing_indent + r'def \w+', code[search_from:]):
        end_markers.append(search_from + em.start())
        break
    
    for pattern in ['\n' + ' ' * (existing_indent + 4) + 'result = iron_classify',
                    '\n' + ' ' * existing_indent + 'result = iron_classify']:
        pos = code.find(pattern, search_from)
        if pos >= 0:
            end_markers.append(pos)
    
    for pattern in ['\n' + ' ' * existing_indent + 'all_lines',
                    '\n' + ' ' * existing_indent + 'header_line',
                    '\n' + ' ' * existing_indent + 'results =']:
        pos = code.find(pattern, search_from)
        if pos >= 0:
            end_markers.append(pos)
    
    if not end_markers:
        return line_start, None, existing_indent
    
    func_end_pos = min(end_markers)
    return line_start, func_end_pos, existing_indent

def apply_v5_changes(code, is_batch):
    line_start, func_end_pos, existing_indent = find_iron_classify_bounds(code)
    if func_end_pos is None:
        print("  WARNING: Could not find end of iron_classify")
        return code
    
    v5_lines = v5_func_code.split('\n')
    v5_indented_lines = []
    for line in v5_lines:
        if line.strip():
            v5_indented_lines.append(' ' * existing_indent + line)
        else:
            v5_indented_lines.append(line)
    v5_indented = '\n'.join(v5_indented_lines)
    
    code = code[:line_start] + v5_indented + code[func_end_pos:]
    print(f"  Replaced iron_classify with V5 (indent={existing_indent})")
    
    if not is_batch:
        old_handler_patterns = [
            r'([ \t]*)result = iron_classify\(text\)\n([ \t]*)if result:\n([ \t]*)ptype, sentiment,\s*(?:iron_)?priority = result\n([ \t]*)source = [\'"]\u94c1\u5f8b\u62e6\u622a[\'"]',
        ]
        for pat in old_handler_patterns:
            old_handler = re.search(pat, code)
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
                code = code[:old_handler.start()] + new_handler + code[old_handler.end():]
                print(f"  Replaced result handler (single-feedback)")
                break
    else:
        old_handler = re.search(
            r'([ \t]*)result = iron_classify\(feedback_text\)\n([ \t]*)if result:\n([ \t]*)ptype, sentiment,\s*(?:iron_)?priority = result\n([ \t]*)else:\n([ \t]*)ptype = [\'"]\u4f53\u9a8c[\'"]\n([ \t]*)sentiment = [\'"]\u4e2d\u6027[\'"]\n([ \t]*)priority = [\'"]\u4f4e[\'"]',
            code
        )
        if old_handler:
            base = old_handler.group(1)
            inner_if = old_handler.group(2)
            inner_if2 = old_handler.group(3)
            inner_else = old_handler.group(4)
            inner_else2 = old_handler.group(5)
            inner_else3 = old_handler.group(6)
            inner_else4 = old_handler.group(7)
            
            new_handler = (
                f"{base}result = iron_classify(feedback_text)\n"
                f"{inner_if}if result:\n"
                f"{inner_if2}ptype, sentiment, iron_priority = result\n"
                f"{inner_if2}priority = iron_priority if iron_priority is not None else '\u4f4e'\n"
                f"{inner_else}else:\n"
                f"{inner_else2}ptype = '\u4f53\u9a8c'\n"
                f"{inner_else3}sentiment = '\u4e2d\u6027'\n"
                f"{inner_else4}priority = '\u4f4e'"
            )
            code = code[:old_handler.start()] + new_handler + code[old_handler.end():]
            print(f"  Replaced result handler (batch)")
    
    if not is_batch:
        old_prio = re.search(
            r"([ \t]*)priority = llm_result\.get\('priority',\s*'\u4f4e'\)\n([ \t]*)if priority not in \['\u9ad8',\s*'\u4e2d',\s*'\u4f4e'\]:\n([ \t]*)priority = '\u4f4e'",
            code
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
            code = code[:old_prio.start()] + new_prio + code[old_prio.end():]
            print(f"  Replaced priority handler (single-feedback)")
    
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

print(f"\nStep 2: Found {len(matches)} code nodes with iron_classify")

replacements = []
for i, match in enumerate(matches):
    old_code = match['code_value']
    is_batch = 'result = iron_classify(feedback_text)' in old_code
    node_type = "batch" if is_batch else "single-feedback"
    print(f"\n--- Node {i+1} ({node_type}) ---")
    
    # Step 3: Fix all known bugs
    fixed_code = fix_all_bugs(old_code)
    
    # Step 4: Iteratively fix remaining broken words
    fixed_code = iterative_fix_broken_words(fixed_code)
    
    ok, err = try_compile(fixed_code)
    if not ok:
        print(f"  FAILED to fix all bugs: {err[:200]}")
        debug_path = f'd:\\产品分析\\SpecMark\\workflow\\_debug_failed_node_{i}.py'
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        print(f"  Saved to: {debug_path}")
        continue
    
    # Step 5: Apply V5 changes
    new_code = apply_v5_changes(fixed_code, is_batch)
    
    # Step 6: Verify V5 code compiles
    ok, err = try_compile(new_code)
    if not ok:
        print(f"  V5 compile FAILED: {err[:200]}")
        debug_path = f'd:\\产品分析\\SpecMark\\workflow\\_debug_v5_failed_node_{i}.py'
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"  Saved to: {debug_path}")
        continue
    
    print(f"  V5 compile: OK")
    new_yaml_value = code_to_yaml_single_line(new_code)
    replacements.append({
        'quote_start': match['quote_start'],
        'end_pos': match['end_pos'],
        'new_yaml_value': new_yaml_value,
    })
    print(f"  Ready to replace (YAML value length: {len(new_yaml_value)})")

# Step 7: Apply replacements from end to start
replacements.sort(key=lambda x: x['quote_start'], reverse=True)
for r in replacements:
    raw_text = raw_text[:r['quote_start']] + r['new_yaml_value'] + raw_text[r['end_pos']:]
    print(f"\nApplied replacement at position {r['quote_start']}")

with open(YAML_PATH, 'w', encoding='utf-8') as f:
    f.write(raw_text)

print("\nStep 8: Final validation...")

try:
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        test_data = yaml.safe_load(f)
    print("YAML parse: OK")
    
    test_nodes = test_data['workflow']['graph']['nodes']
    all_ok = True
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
                has_textor = 'textor' in code
                has_ifre = 'ifre.search' in code
                
                ok, err = try_compile(code)
                
                print(f"  {title}:")
                print(f"    V5={has_none}, iron_priority={has_iron_priority}")
                print(f"    bugs: prioritynot={has_prioritynot}, stray_n={has_stray_n}, textor={has_textor}, ifre={has_ifre}")
                print(f"    compile={'OK' if ok else 'FAIL'}")
                if not ok:
                    all_ok = False
                    print(f"    error: {err[:200]}")
except Exception as e:
    print(f"YAML validation FAILED: {e}")
    all_ok = False

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()
max_line = max(len(line) for line in lines)
print(f"\nLongest line: {max_line} chars")

if all_ok:
    print("\n=== ALL CHECKS PASSED ===")
else:
    print("\n=== SOME CHECKS FAILED ===")
