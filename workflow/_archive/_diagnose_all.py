import yaml
import re
import py_compile
import tempfile
import os

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data['workflow']['graph']['nodes']
issues_found = []

for node in nodes:
    nd = node.get('data', {})
    if nd.get('type') != 'code' or 'code' not in nd:
        continue
    code = nd['code']
    title = nd.get('title', '?')
    
    print(f"\n{'='*60}")
    print(f"Node: {title}")
    print(f"{'='*60}")
    
    # 1. Check for broken words (spaces inside identifiers/strings)
    broken_patterns = [
        (r"'[^']*\s[^']*'", "Possible broken string (space inside short string)"),
    ]
    
    # Check for specific known breakages from line continuation
    suspicious = re.findall(r"'[^']{1,10}\s[^']{1,10}'", code)
    if suspicious:
        for s in suspicious:
            if s not in ["'铁律拦截'", "'invalid_input'", "'功能问题'", "'性能问题'", "'体验问题'", "'内容问题'"]:
                print(f"  SUSPICIOUS STRING: {s}")
                issues_found.append(f"{title}: {s}")
    
    # 2. Try to compile the code
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        py_compile.compile(tmp_path, doraise=True)
        print(f"  Python compile: OK")
        os.unlink(tmp_path)
    except py_compile.PyCompileError as e:
        print(f"  Python compile: FAILED")
        print(f"  Error: {e}")
        issues_found.append(f"{title}: Compile error - {e}")
        os.unlink(tmp_path)
    
    # 3. Check indentation consistency
    lines = code.split('\n')
    indent_issues = []
    for i, line in enumerate(lines, 1):
        if line.strip() and not line.startswith('#'):
            leading = len(line) - len(line.lstrip())
            if leading % 4 != 0 and leading % 2 != 0:
                indent_issues.append(f"Line {i}: indent={leading} '{line[:50]}'")
    if indent_issues:
        print(f"  Indentation issues ({len(indent_issues)}):")
        for issue in indent_issues[:5]:
            print(f"    {issue}")
        issues_found.extend(indent_issues)
    else:
        print(f"  Indentation: OK")
    
    # 4. Check iron_classify specific issues
    if 'iron_classify' in code:
        # Check function indentation
        func_match = re.search(r'def iron_classify\(text\):', code)
        if func_match:
            func_line_start = code[:func_match.start()].count('\n') + 1
            func_indent = func_match.start() - code[:func_match.start()].rfind('\n') - 1
            print(f"  iron_classify indent: {func_indent} spaces")
            
            # Check if function body indentation is consistent
            func_body_start = func_match.end()
            next_lines = code[func_body_start:func_body_start+500].split('\n')
            for j, line in enumerate(next_lines[1:4], 1):
                if line.strip():
                    body_indent = len(line) - len(line.lstrip())
                    print(f"    Body line {j} indent: {body_indent} '{line[:40]}'")
        
        # Check iron_priority usage
        if 'iron_priority' in code:
            print(f"  iron_priority: FOUND")
        else:
            print(f"  iron_priority: MISSING!")
            issues_found.append(f"{title}: iron_priority missing")
        
        # Check for old priority variable
        if re.search(r'ptype,\s*sentiment\s*,\s*priority\s*=\s*result', code):
            print(f"  OLD 'priority = result': STILL PRESENT!")
            issues_found.append(f"{title}: old priority=result still present")

print(f"\n\n{'='*60}")
print(f"TOTAL ISSUES FOUND: {len(issues_found)}")
for issue in issues_found:
    print(f"  - {issue}")
