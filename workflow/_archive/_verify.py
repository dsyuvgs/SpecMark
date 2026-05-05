# _verify.py — 全面验证补丁后的工作流

import re, hashlib, yaml

with open('SpecMark最新.yml', 'r', encoding='utf-8') as f:
    content = f.read()

print('=' * 60)
print('验证报告: SpecMark最新.yml (v6.2)')
print('=' * 60)

# 1. YAML 合法性
try:
    yaml.safe_load(content)
    print('[OK] YAML 解析通过')
except Exception as e:
    print(f'[FAIL] YAML 解析失败: {e}')

# 2. 三个 iron_classify 一致性
ms = list(re.finditer(r'def iron_classify\(text\):(.*?)return None', content, re.DOTALL))
hashes = [hashlib.sha256(m.group(1).encode()).hexdigest()[:16] for m in ms]
all_same = len(set(hashes)) == 1
print(f'[{"OK" if all_same else "FAIL"}] iron_classify 一致性: {len(ms)} 个, hashes={hashes}')

# 3. 三个 apply_priority_rules 一致性
ms2 = list(re.finditer(r'def apply_priority_rules\(text, ptype, priority\):(.*?)return priority', content, re.DOTALL))
hashes2 = [hashlib.sha256(m.group(1).encode()).hexdigest()[:16] for m in ms2]
all_same2 = len(set(hashes2)) == 1
print(f'[{"OK" if all_same2 else "FAIL"}] apply_priority_rules 一致性: {len(ms2)} 个, hashes={hashes2}')

# 4. 无 None 优先级残留
nones = re.findall(r'return\s*\([^)]*None[^)]*\)', content)
print(f'[{"OK" if not nones else "FAIL"}] return (...None): {len(nones)} 处')

# 5. 版本标记
v61 = len(re.findall(r'iron_classify v6\.1', content))
v62 = len(re.findall(r'apply_priority_rules v6\.2', content))
print(f'[INFO] iron_classify v6.1: {v61} 处, apply_priority_rules v6.2: {v62} 处')

# 6. 调用链路完整性
iron_calls = len(re.findall(r'result = iron_classify\(', content))
apply_calls_text = len(re.findall(r'apply_priority_rules\(text,', content))
apply_calls_fb = len(re.findall(r'apply_priority_rules\(feedback_text,', content))
print(f'[INFO] iron_classify 调用: {iron_calls} 处')
print(f'[INFO] apply_priority_rules(text: {apply_calls_text} 处')
print(f'[INFO] apply_priority_rules(feedback: {apply_calls_fb} 处')

# 7. 花里胡哨 typo
hhs = len(re.findall(r'花里花哨', content))
hhs_correct = len(re.findall(r'花里胡哨', content))
print(f'[{"OK" if hhs == 0 else "FAIL"}] 花里花哨 typo: {hhs} 处, 花里胡哨: {hhs_correct} 处')

print('=' * 60)
all_ok = all_same and all_same2 and not nones and hhs == 0
print(f'总体评估: {"✅ 通过" if all_ok else "❌ 存在问题"}')
