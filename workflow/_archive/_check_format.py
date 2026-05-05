import yaml

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

max_line_len = 0
max_line_num = 0
for i, line in enumerate(lines, 1):
    if len(line) > max_line_len:
        max_line_len = len(line)
        max_line_num = i

print(f"Longest line: line {max_line_num}, length {max_line_len}")

# Check lines > 10000 chars
long_lines = [(i+1, len(line)) for i, line in enumerate(lines) if len(line) > 10000]
print(f"\nLines > 10000 chars: {len(long_lines)}")
for num, length in long_lines[:5]:
    print(f"  Line {num}: {length} chars")

# Check if code fields are on single lines
for i, line in enumerate(lines, 1):
    if line.strip().startswith('code:'):
        print(f"\n  Line {i} starts with 'code:': length={len(line)}")
        if len(line) > 50000:
            print(f"    WARNING: Very long single-line code field!")

# Also check the original backup for comparison
BACKUP_PATH = YAML_PATH + '.v5bak6'
with open(BACKUP_PATH, 'r', encoding='utf-8') as f:
    backup_lines = f.readlines()

backup_max = max(len(line) for line in backup_lines)
print(f"\nBackup longest line: {backup_max}")

# Check if original had line continuations
continuation_count = 0
for i, line in enumerate(backup_lines):
    if line.rstrip().endswith('\\'):
        continuation_count += 1
print(f"Backup lines ending with '\\': {continuation_count}")

continuation_count_new = 0
for i, line in enumerate(lines):
    if line.rstrip().endswith('\\'):
        continuation_count_new += 1
print(f"New file lines ending with '\\': {continuation_count_new}")
