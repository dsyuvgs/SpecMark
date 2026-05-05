import re
import yaml

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    yaml_text = f.read()

def extract_yaml_string(text, start_pos):
    i = start_pos
    if text[i] != '"':
        return None, start_pos
    i += 1
    result = []
    while i < len(text):
        ch = text[i]
        if ch == '\\' and i + 1 < len(text):
            next_ch = text[i + 1]
            if next_ch == '"':
                result.append('"')
                i += 2
            elif next_ch == '\\':
                result.append('\\')
                i += 2
            elif next_ch == 'n':
                result.append('\n')
                i += 2
            elif next_ch == 't':
                result.append('\t')
                i += 2
            else:
                result.append('\\')
                result.append(next_ch)
                i += 2
        elif ch == '"':
            return ''.join(result), i + 1
        else:
            result.append(ch)
            i += 1
    return None, start_pos

code_pattern = re.compile(r'(\s+code:\s*)"')
for i, match in enumerate(code_pattern.finditer(yaml_text)):
    quote_start = match.end() - 1
    code_str, end_pos = extract_yaml_string(yaml_text, quote_start)
    if code_str is None:
        print(f'Node {i}: FAILED to extract at pos {quote_start}')
        continue
    has_iron = 'iron_classify' in code_str
    print(f'Node {i}: code_len={len(code_str)}, has_iron={has_iron}, end_pos={end_pos}')
    if has_iron:
        print(f'  First 200: {repr(code_str[:200])}')
        iron_match = re.search(r'def iron_classify\(text\):.*?return None', code_str, re.DOTALL)
        print(f'  iron_classify pattern match: {iron_match is not None}')

        result_handler = re.search(
            r"result\s*=\s*iron_classify\(text\)\s+if\s+result:\s+ptype,\s*sentiment\s*,\s*priority\s*=\s*result\s+source\s*=\s*'铁律拦截'",
            code_str, re.DOTALL
        )
        print(f'  result handler match: {result_handler is not None}')

        prio_handler = re.search(
            r"priority\s*=\s*llm_result\.get\('priority',\s*'低'\)",
            code_str
        )
        print(f'  priority handler match: {prio_handler is not None}')

        print(f'  Last 200: {repr(code_str[-200:])}')
