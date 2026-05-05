import yaml
import re
import py_compile
import tempfile
import os

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'
BACKUP_PATH = YAML_PATH + '.v5bak6'

print("=== CURRENT FILE ===")
with open(YAML_PATH, 'r', encoding='utf-8') as f:
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
    
    # Try to compile
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        py_compile.compile(tmp_path, doraise=True)
        print(f"{title}: COMPILE OK")
    except py_compile.PyCompileError as e:
        print(f"{title}: COMPILE FAILED - {e}")
    finally:
        os.unlink(tmp_path)

print("\n=== ORIGINAL BACKUP ===")
with open(BACKUP_PATH, 'r', encoding='utf-8') as f:
    data_bak = yaml.safe_load(f)

nodes_bak = data_bak['workflow']['graph']['nodes']
for node in nodes_bak:
    nd = node.get('data', {})
    if nd.get('type') != 'code' or 'code' not in nd:
        continue
    code = nd['code']
    title = nd.get('title', '?')
    if 'iron_classify' not in code:
        continue
    
    # Try to compile
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        py_compile.compile(tmp_path, doraise=True)
        print(f"{title}: COMPILE OK")
    except py_compile.PyCompileError as e:
        print(f"{title}: COMPILE FAILED - {e}")
    finally:
        os.unlink(tmp_path)
    
    # Show iron_classify indentation
    func_match = re.search(r'def iron_classify\(text\):', code)
    if func_match:
        before = code[:func_match.start()]
        last_newline = before.rfind('\n')
        if last_newline >= 0:
            def_line_indent = len(code[last_newline+1:func_match.start()])
        else:
            def_line_indent = func_match.start()
        
        func_body = code[func_match.end():func_match.end()+300]
        body_lines = func_body.split('\n')
        print(f"  def iron_classify indent: {def_line_indent}")
        for i, line in enumerate(body_lines[:5]):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                print(f"  Body line {i}: indent={indent} | {repr(line[:60])}")
