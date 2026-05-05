# _fix_indent.py — 修复 def apply_priority_rules 缩进

with open('SpecMark最新.yml', 'r', encoding='utf-8') as f:
    content = f.read()

# 把行首的 def apply_priority_rules 加上18空格缩进
content = content.replace('\ndef apply_priority_rules(text, ptype, priority):', '\n                  def apply_priority_rules(text, ptype, priority):')

with open('SpecMark最新.yml', 'w', encoding='utf-8') as f:
    f.write(content)

import re
count = len(re.findall(r'^def apply_priority_rules', content, re.MULTILINE))
print(f'行首 def apply_priority_rules 残留: {count} 处 (应为0)')

# 验证 YAML
import yaml
try:
    yaml.safe_load(content)
    print('YAML 解析: OK')
except Exception as e:
    print(f'YAML 解析: FAIL - {e}')
