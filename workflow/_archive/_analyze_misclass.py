# _analyze_misclass.py — 分析高→中误判模式

import csv, re

GOLD_CSV = r'd:\产品分析\个人标注.txt'

feedbacks = []
with open(GOLD_CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader, None)
    for row in reader:
        if len(row) >= 5:
            gold_type = row[2].strip()
            if gold_type.endswith('问题'):
                gold_type = gold_type[:-2]
            feedbacks.append({
                'idx': row[0].strip(),
                'text': row[1].strip(),
                'gold_type': gold_type,
                'gold_sentiment': row[3].strip(),
                'gold_priority': row[4].strip(),
            })

# Import the test functions
exec(open('_v6_test.py', 'r', encoding='utf-8').read().split('# === Test ===')[0])

print("=== 高→中 误判分析 ===\n")
count = 0
by_type = {}
for fb in feedbacks:
    result = iron_classify_v6(fb['text'])
    if result:
        ptype, sentiment, priority = result
        priority = apply_priority_rules(fb['text'], ptype, priority)
        if fb['gold_priority'] == '高' and priority == '中':
            count += 1
            key = ptype
            if key not in by_type:
                by_type[key] = []
            by_type[key].append(fb['text'][:80])

print(f"总计: {count} 条\n")
for k, v in sorted(by_type.items(), key=lambda x: -len(x[1])):
    print(f"--- {k} ({len(v)}条) ---")
    for t in v[:10]:
        print(f"  '{t}'")
    if len(v) > 10:
        print(f"  ... 还有 {len(v)-10} 条")
    print()

print("\n=== 中→低 误判分析 ===\n")
count2 = 0
by_type2 = {}
for fb in feedbacks:
    result = iron_classify_v6(fb['text'])
    if result:
        ptype, sentiment, priority = result
        priority = apply_priority_rules(fb['text'], ptype, priority)
        if fb['gold_priority'] == '中' and priority == '低':
            count2 += 1
            key = ptype
            if key not in by_type2:
                by_type2[key] = []
            by_type2[key].append(fb['text'][:80])

print(f"总计: {count2} 条\n")
for k, v in sorted(by_type2.items(), key=lambda x: -len(x[1])):
    print(f"--- {k} ({len(v)}条) ---")
    for t in v[:10]:
        print(f"  '{t}'")
    if len(v) > 10:
        print(f"  ... 还有 {len(v)-10} 条")
    print()
