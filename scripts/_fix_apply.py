import re

with open('workflow/SpecMark最新.yml', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: find apply_priority_rules defined inside iron_classify (after return None)
# and move it outside iron_classify but inside main

# The pattern to find:
# 1. "return None" followed by newline
# 2. Then "def apply_priority_rules" with its body
# 3. Then blank line before "result = iron_classify"

old_pattern = r'(                  return None\n)(                  def apply_priority_rules\(text, ptype, priority\):\n)(.*?)(                  return priority\n\n\n)'

def fix_match(m):
    before = m.group(1)  # "                  return None\n"
    func_def = m.group(2)  # "                  def apply_priority_rules..."
    func_body = m.group(3)  # function body
    after = m.group(4)  # "                  return priority\n\n\n"
    
    # Re-indent function body to be at main level (same as iron_classify)
    # Currently at 18 spaces (inside iron_classify), need to be at 14 spaces (inside main)
    # Actually, looking at the code, iron_classify is at 14 spaces, and its body is at 18 spaces
    # apply_priority_rules should be at 14 spaces (same level as iron_classify)
    
    # The function def line is at 18 spaces, need to move to 14
    new_func_def = func_def[4:]  # remove 4 leading spaces
    # The function body lines are at 22 spaces, need to move to 18
    new_func_body = '\n'.join(line[4:] if line.startswith('                    ') else line for line in func_body.split('\n'))
    # The return priority line is at 22 spaces, need to move to 18
    new_after = after[4:]  # remove 4 leading spaces from "                  return priority\n\n\n"
    
    return before + '\n' + new_func_def + new_func_body + new_after

content = re.sub(old_pattern, fix_match, content, flags=re.DOTALL)

with open('workflow/SpecMark最新.yml', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. Checking...')

# Verify
with open('workflow/SpecMark最新.yml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def apply_priority_rules' in line:
        indent = len(line) - len(line.lstrip())
        print(f'Line {i+1}: apply_priority_rules at indent {indent}: {line.rstrip()}')
    if 'def iron_classify' in line:
        indent = len(line) - len(line.lstrip())
        print(f'Line {i+1}: iron_classify at indent {indent}: {line.rstrip()}')
