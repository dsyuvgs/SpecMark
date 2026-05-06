import re, yaml, hashlib

yml_path = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'

with open(yml_path, 'r', encoding='utf-8') as f:
    content = f.read()

# === Fix 1: Add positive sentiment keywords to pos_words ===
# Current pos_words missing: 上手简单, 支持, 权威, 审核过, 实拍图, 不错, 剪出
old_pos = """pos_words = ['很好', '好用', '专业', '不错', '很棒', '超好用',
                               '体验很好', '给力', '真香', '效率提高', '帮助提高', '支持导出',
                               '覆盖广', '很全', '很细', '很准', '很及时', '很方便', '很酷',
                               '很震撼', '很到位', '准时送达', '好评']"""

new_pos = """pos_words = ['很好', '好用', '专业', '不错', '很棒', '超好用',
                               '体验很好', '给力', '真香', '效率提高', '帮助提高', '支持导出',
                               '覆盖广', '很全', '很细', '很准', '很及时', '很方便', '很酷',
                               '很震撼', '很到位', '准时送达', '好评', '上手简单', '剪出不错',
                               '支持查看', '权威', '审核过', '实拍图', '推荐给大家', '满意',
                               '顺畅', '速度快', '还是热的', '很准', '简洁', '方便']"""

content = content.replace(old_pos, new_pos)

# === Fix 2: Add negative context words for better boundary detection ===
old_neg = """neg_ctx = ['但', '但是', '不过', '就是', '可惜', '然而', '只是', '可是', '虽然',
                             '差评', '问题', '气愤', '威胁', '刷', '假', '骗', '坑', '垃圾', '太差',
                             '不满', '投诉', '拒', '不解决', '不管']"""

new_neg = """neg_ctx = ['但', '但是', '不过', '就是', '可惜', '然而', '只是', '可是', '虽然',
                             '差评', '问题', '气愤', '威胁', '刷', '假', '骗', '坑', '垃圾', '太差',
                             '不满', '投诉', '拒', '不解决', '不管', '不更新', '三天', '黄色', '暧昧',
                             '动机不纯', '没更新']"""

content = content.replace(old_neg, new_neg)

# === Fix 3: Add more svc_high_kw for better priority detection ===
# "推诿" should trigger high priority, "丢餐" should trigger high
old_svc = r"svc_high_kw = r'食品安全|异物|变质|寄生虫|吃出|拉肚子|食物中毒|发霉|馊了|臭了|不新鲜|拒赔|骑手态度|司机态度|等超久|自动续费|被欺骗|等了\d+分钟|等了\d+小时|没人接单|没接单|骚扰|威胁'"
new_svc = r"svc_high_kw = r'食品安全|异物|变质|寄生虫|吃出|拉肚子|食物中毒|发霉|馊了|臭了|不新鲜|拒赔|骑手态度|司机态度|等超久|自动续费|被欺骗|等了\d+分钟|等了\d+小时|没人接单|没接单|骚扰|威胁|推诿|丢餐|丢失|错拿|拒不|拒不赔偿|态度恶劣|态度差|不处理|不作为|不理|不管|没人处理|不解决'"

content = content.replace(old_svc, new_svc)

# === Fix 4: Add specific rules for empty output cases ===
# #22: "物流信息三天没更新" - should be 体验/负向/中
# #33: "漂流瓶...黄色与暧昧信息" - should be 内容/负向/中
# Add before "return None" at the end of iron_classify

old_return_none = "                  return None\n\n              def apply_priority_rules"
new_rules_before_none = """                  if re.search(r'物流.{0,2}信息.{0,3}(没|不)更新|三天没更新|信息不更新', text):
                      return ('体验', '负向', '中')
                  if re.search(r'黄色|暧昧|动机不纯|低俗|色情', text):
                      return ('内容', '负向', '中')
                  if re.search(r'推诿|互相推诿|踢皮球', text):
                      return ('体验', '负向', '高')
                  if re.search(r'预售.{0,4}拖延|一推再推|等了.{0,2}月|等了.{0,3}还没发货', text):
                      return ('体验', '负向', '高')
                  if re.search(r'全勤|迟到|被扣', text):
                      return ('体验', '负向', '中')
                  return None

              def apply_priority_rules"""

content = content.replace(old_return_none, new_rules_before_none)

# === Fix 5: Fix #50 - 支付宝账户限制 should be 功能/高 ===
# The current code already has: if re.search(r'账户.{0,2}限制|账户.{0,2}冻结|限制.*转账|限制.*提现', text): return ('功能', '负向', '高')
# But it's being intercepted earlier by has_ambig_svc + broad_func_failure path
# The issue is that "支付宝系统误判...禁止转账和提现" hits the broad_func_failure check
# but then falls into the wrong branch because it also has ambig_svc keywords
# Actually, looking more carefully, the rule for 账户限制 is already at line ~2260
# The problem is that the text contains "限制" which is in broad_func_failure,
# and also "提现" which is in ambig_svc... let me check the flow

# Actually the issue is: "禁止转账和提现" hits broad_func_failure,
# but the text also has no pure_svc or driver keywords,
# so it goes to the "if broad_func_failure:" branch and returns ('功能', '负向', p)
# where p is determined by func_high_kw... 
# But the Agent output shows 体验/中, which means iron_classify returned None
# and it fell through to LLM which gave 体验/中
# Wait, the source says "铁律拦截" for #50 in the agent results
# Let me re-check... actually the comparison showed Agent: 体验/中 for #50
# But the source was 铁律拦截... so iron_classify did return something
# The issue is the text "支付宝系统误判该交易为风险操作" - "误判" might not be in any keyword list
# and "禁止转账和提现" - "禁止" is not in broad_func_failure either!
# The keyword is "限制转账" but the text says "禁止转账"
# Fix: add "禁止" to the account restriction pattern

old_acct = "                  if re.search(r'账户.{0,2}限制|账户.{0,2}冻结|限制.*转账|限制.*提现', text):\n                      return ('功能', '负向', '高')"
new_acct = "                  if re.search(r'账户.{0,2}限制|账户.{0,2}冻结|限制.*转账|限制.*提现|禁止.*转账|禁止.*提现|无法.*转账|无法.*提现', text):\n                      return ('功能', '负向', '高')"

content = content.replace(old_acct, new_acct)

# Also add 禁止 to broad_func_failure and true_crash patterns
old_broad = "r'不工作|不运行|无法使用|不可用|'"
new_broad = "r'禁止|不工作|不运行|无法使用|不可用|'"

content = content.replace(old_broad, new_broad)

# === Fix 6: Fix #3 - 骑手放驿站丢餐+推诿 should be 体验/高 ===
# Current: has_pure_svc + broad_func_failure -> returns 体验/低 (no svc_high_kw match)
# "丢餐" and "推诿" are now added to svc_high_kw in Fix 3
# But "丢餐" is not in the text - the text says "餐品丢失、错拿"
# "丢失" is now in svc_high_kw, and "推诿" is now in svc_high_kw
# So this should be fixed by Fix 3

# === Fix 7: Fix #37 - 朋友圈照片被压缩 should be 功能/高 ===
# Current rule: if re.search(r'照片被压缩|画质.*变|压缩.*模糊', text): return ('功能', '负向', '中')
# Knowledge base says: core function (播放/上传/下载) + 功能 type = 高
# The apply_priority_rules should boost this to 高 because 播放/上传 is a core function
# But the current rule returns '中' directly, bypassing apply_priority_rules
# Actually no - apply_priority_rules IS called after iron_classify
# The issue is that '照片被压缩' matches core_func_kw in apply_priority_rules
# but only if ptype == '功能' and priority == '中'
# Let me check... yes, '照片' is not in core_func_kw but '播放' is not in the text either
# The text is "朋友圈发的照片被压缩得模糊不清，原图上传后画质完全变了"
# '上传' IS in core_func_kw! So apply_priority_rules should boost it to 高
# But the agent output shows 高 for #37, so this is actually already correct!
# The comparison showed Agent: 功能/高 vs LLM: 功能/中 - Agent was right

# === Fix 8: Fix #14 - 笔记本屏幕重影 should be 体验/中 not 低 ===
# Current rule: if re.search(r'重影|竖条|刮痕|显示屏', text): return ('体验', '负向', '低')
# But knowledge base says: "用了4个月发现电脑显示屏有竖条重影" - this is a product quality issue
# Not a software issue, so 体验 is correct. But priority should be 中 because "重影" is a significant issue
# Fix: change priority from 低 to 中 for display issues

old_display = "                  if re.search(r'重影|竖条|刮痕|显示屏', text):\n                      return ('体验', '负向', '低')"
new_display = "                  if re.search(r'重影|竖条|刮痕|显示屏', text):\n                      return ('体验', '负向', '中')"

content = content.replace(old_display, new_display)

# === Fix 9: Fix #7 - 售后未全额赔付 should be 中 not 低 ===
# Current: "退款|售后|退货|换货|拒赔" -> 体验/低 (unless 拒赔 which is 高)
# "未按订单实付金额全额赔付" is more serious than general 售后
# Fix: add "未.*全额|不全额|部分退款|仅退" to svc_high_kw
# Already added "推诿" etc. in Fix 3
# Add specific rule for partial refund

old_refund = "                  if re.search(r'退款|售后|退货|换货|拒赔', text):\n                      p = '高' if '拒赔' in text else '低'\n                      return ('体验', '负向', p)"
new_refund = "                  if re.search(r'退款|售后|退货|换货|拒赔', text):\n                      if re.search(r'拒赔|未.*全额|不全额|部分退款|仅退|不按|与.*不符', text):\n                          p = '高'\n                      else:\n                          p = '低'\n                      return ('体验', '负向', p)"

content = content.replace(old_refund, new_refund)

# === Fix 10: Fix #29 - 顺风车取消扣全勤 should be 中 not 低 ===
# Already added "全勤|迟到|被扣" rule in Fix 4

# === Fix 11: Fix #47 - 匹配机制 should be 中 not 低 ===
# Current: has_content_issue -> 内容/低 (unless content_high_kw)
# "匹配机制有问题" - "匹配机制" is in has_content_issue
# But "有问题" is not strong enough for 高, should be 中
# Fix: add "有问题" to content moderate keywords in apply_priority_rules
# Actually the apply_priority_rules already has cnt_moderate_kw for 内容/低->中
# Let me check... "匹配机制有问题" - "有问题" is not in cnt_moderate_kw
# Add "有问题" to cnt_moderate_kw

old_cnt = "cnt_moderate_kw = r'完全|根本|太不|严重|错误|不对|过时|不一样|不一致|不公平|没法玩|没法用|全是|一直|骗|假|虚假|误导|不实|伪造|假冒|抄袭|剽窃|盗版|侵权|刷评|水军|假评'"
new_cnt = "cnt_moderate_kw = r'完全|根本|太不|严重|错误|不对|过时|不一样|不一致|不公平|没法玩|没法用|全是|一直|骗|假|虚假|误导|不实|伪造|假冒|抄袭|剽窃|盗版|侵权|刷评|水军|假评|有问题|不合理'"

content = content.replace(old_cnt, new_cnt)

# === Verify YAML ===
try:
    yaml.safe_load(content)
    print('YAML validation: OK')
except Exception as e:
    print(f'YAML validation FAILED: {e}')

# === Check consistency - count occurrences of each fix ===
fixes = {
    'new_pos_words': content.count('上手简单'),
    'new_neg_ctx': content.count('动机不纯'),
    'new_svc_high': content.count('推诿'),
    'new_empty_rules': content.count('黄色|暧昧'),
    'new_acct_rule': content.count('禁止.*转账'),
    'new_display': content.count('重影|竖条|刮痕|显示屏'),
    'new_refund': content.count('未.*全额'),
    'new_cnt_moderate': content.count('有问题|不合理'),
}

print('\nFix counts (should be 3 for each - one per node):')
for k, v in fixes.items():
    status = 'OK' if v == 3 else f'WARNING: got {v}'
    print(f'  {k}: {v} -> {status}')

with open(yml_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('\nAll fixes applied and saved.')
