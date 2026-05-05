import csv

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
                'text': row[1].strip(),
                'gold_type': gold_type,
                'gold_sentiment': row[3].strip(),
                'gold_priority': row[4].strip(),
            })

# Gold priority distribution
prio_dist = {}
for fb in feedbacks:
    p = fb['gold_priority']
    prio_dist[p] = prio_dist.get(p, 0) + 1
print("Gold priority distribution:")
for p, c in sorted(prio_dist.items()):
    print(f"  {p}: {c}")

# Gold priority by type
print("\nGold priority by type:")
for t in ['功能', '性能', '体验', '内容']:
    subset = [fb for fb in feedbacks if fb['gold_type'] == t]
    print(f"  {t} ({len(subset)}):")
    for p in ['高', '中', '低']:
        c = sum(1 for fb in subset if fb['gold_priority'] == p)
        if c:
            print(f"    {p}: {c}")

# Check: how many gold=高 are 功能 type?
high_func = [fb for fb in feedbacks if fb['gold_priority'] == '高' and fb['gold_type'] == '功能']
print(f"\nGold=高 + 功能: {len(high_func)}")
# Show some
for fb in high_func[:5]:
    print(f"  '{fb['text'][:70]}'")
