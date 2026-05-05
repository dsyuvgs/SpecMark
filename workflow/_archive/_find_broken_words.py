import yaml
import re

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
        
        # Find ALL broken words: word boundaries that are missing spaces
        # Pattern: a word char followed by a keyword like 'or', 'and', 'in', 'not', 'if', 'for'
        broken = re.findall(r'\w+(or|and|in|not|if|for|is|as)\b', code)
        for b in set(broken):
            if len(b) < len(b) + 1:  # only show if it's a merged word
                pass
            # Find actual occurrences
            for m in re.finditer(r'(\w{2,})(or|and|in|not|if|for|is|as)\b', code):
                word = m.group(0)
                if word not in ['iron', 'login', 'margin', 'begin', 'within', 'without', 'cannot',
                                'main', 'chain', 'obtain', 'sustain', 'refrain', 'certain',
                                'contain', 'maintain', 'ascertain', 'determine', 'examine',
                                'domain', 'remain', 'explain', 'complain', 'refine',
                                'define', 'confine', 'decline', 'combine', 'assign',
                                'design', 'resign', 'consign', 'align', 'signal',
                                'origin', 'imagine', 'doctrine', 'routine', 'imagine',
                                'opinion', 'impose', 'expose', 'dispose', 'compose',
                                'propose', 'suppose', 'oppose', 'purpose', 'impulse',
                                'reconcile', 'principle', 'discipline', 'multiple',
                                'map', 'maps', 'mapping', 'mappings']:
                    # Check if it's actually a broken word by looking at context
                    start = max(0, m.start() - 20)
                    end = min(len(code), m.end() + 20)
                    context = code[start:end]
                    # Only flag if it looks like Python code with missing space
                    if re.search(r'\w+(or|and|in|not)\b', word) and len(word) > 4:
                        print(f"  POSSIBLE BROKEN: '{word}' at pos {m.start()}")
                        print(f"    Context: {repr(context)}")
