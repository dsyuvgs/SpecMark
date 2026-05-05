import yaml
import re
import py_compile
import tempfile
import os

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml.v5bak6'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

nodes = data['workflow']['graph']['nodes']
for node in nodes:
    nd = node.get('data', {})
    if nd.get('type') == 'code' and 'code' in nd:
        code = nd['code']
        title = nd.get('title', '?')
        if title not in ('反馈规则引擎', '场景JSON解析与更新'):
            continue
        
        print(f"\n=== {title} ===")
        
        # Apply current fixes
        # Fix stray 'n' at line start
        lines = code.split('\n')
        fixed_lines = []
        for line in lines:
            m = re.match(r'^n(\s{4,}(?:def|return|if|for|while|try|except|with|class|assert|pass|break|continue|raise|results|else|elif))', line)
            if m:
                fixed_lines.append(line[1:])
            else:
                fixed_lines.append(line)
        code = '\n'.join(fixed_lines)
        
        # Fix stray 'n' at line end after closing quote
        code = re.sub(r'\}("|\')n\n', r'}\1\n', code)
        
        # Fix missing spaces in keywords
        code = code.replace('prioritynot ', 'priority not ')
        code = code.replace('sentimentnot ', 'sentiment not ')
        code = code.replace('forpattern,', 'for pattern,')
        code = code.replace('returnneed', 'return need')
        code = code.replace('textor ', 'text or ')
        
        # Fix indentation
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
        
        # Try to compile
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            py_compile.compile(tmp_path, doraise=True)
            print(f"  After all fixes: compile OK")
            os.unlink(tmp_path)
        except py_compile.PyCompileError as e:
            print(f"  After all fixes: compile FAILED")
            print(f"  Error: {e}")
            os.unlink(tmp_path)
            
            # Find the error line and show context
            err_match = re.search(r'line (\d+)', str(e))
            if err_match:
                err_line = int(err_match.group(1))
                code_lines = code.split('\n')
                start = max(0, err_line - 3)
                end = min(len(code_lines), err_line + 3)
                for i in range(start, end):
                    marker = ">>>" if i == err_line - 1 else "   "
                    print(f"  {marker} {i+1}: {repr(code_lines[i][:100])}")
            
            # Save for debugging
            debug_path = f'd:\\产品分析\\SpecMark\\workflow\\_debug_comprehensive_{title}.py'
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"  Saved to: {debug_path}")
