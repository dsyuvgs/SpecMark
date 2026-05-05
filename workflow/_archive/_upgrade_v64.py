# _upgrade_v64.py — v6.4 精准修复（精简版）

import re, yaml

with open('SpecMark最新.yml', 'r', encoding='utf-8') as f:
    content = f.read()

# ===== 1. 扩展 iron_classify 的 svc_high_kw（食安检测）=====
old_svc_high = "svc_high_kw = r'食品安全|异物|变质|寄生虫|拒赔|骑手态度|司机态度|等超久|自动续费|被欺骗|等了\\d+分钟|等了\\d+小时|没人接单|没接单|骚扰|威胁'"
new_svc_high = "svc_high_kw = r'食品安全|异物|变质|寄生虫|吃出|拉肚子|食物中毒|发霉|馊了|臭了|不新鲜|拒赔|骑手态度|司机态度|等超久|自动续费|被欺骗|等了\\d+分钟|等了\\d+小时|没人接单|没接单|骚扰|威胁'"

print(f'svc_high_kw 旧版: {content.count(old_svc_high)} 处')
content = content.replace(old_svc_high, new_svc_high)
print(f'svc_high_kw 新版: {content.count(new_svc_high)} 处')

# ===== 2. 升级 apply_priority_rules v6.3 → v6.4 =====
old_perf_severe = "perf_severe_kw = r'严重|根本|完全|一直|突然|太慢|太卡|没法|不敢|靠不住|错过|来不及|没法用|没法玩|没法看|受不了|忍不了|急用|关键|全错过|全没了|耽误|废了|毁了|完蛋|崩溃边缘|用不下去|没法工作|没法学习|影响工作|影响学习'"
new_perf_severe = "perf_severe_kw = r'严重|根本|完全|一直|突然|太慢|太卡|太大|太短|太严重|很严重|没法|不敢|靠不住|错过|来不及|没法用|没法玩|没法看|受不了|忍不了|急用|关键|全错过|全没了|耽误|废了|毁了|完蛋|崩溃边缘|用不下去|没法工作|没法学习|影响工作|影响学习|断断续续|越来越差|越来越慢|越来越卡|不同步|对不上|等不起|等不了|等不及|太可怕|太吓人|太离谱|太夸张|太差了|太烂了|太垃圾|太恶心|太烦人|太讨厌|太糟糕|太差劲'"

print(f'perf_severe_kw 旧版: {content.count(old_perf_severe)} 处')
content = content.replace(old_perf_severe, new_perf_severe)
print(f'perf_severe_kw 新版: {content.count(new_perf_severe)} 处')

old_exp_moderate = "exp_moderate_kw = r'涨了|翻倍|全是|根本|一直|太慢|太复杂|太繁琐|藏得|找不到|不解决|不处理|没人|不理|不管|骗|虚假|陷阱|套路|坑|差|烂|垃圾|恶心|气死|气炸|火大|无语|失望|寒心|过分|离谱|坑爹|坑人|霸王|欺负|歧视|区别对待|不公平|不一致|不一样|差太多|差远了|差很大|天差地别|趁火打劫|坐地起价|乱收费|多收费|重复收费|隐藏费用|强制消费|捆绑销售|诱导消费|虚假促销|虚假优惠|先涨后降|明降暗涨|货不对板|缺斤少两|以次充好|偷工减料|敷衍|推诿|踢皮球|不负责|不作为|不专业|不礼貌|态度恶劣|态度差|骂人|辱骂|威胁|恐吓|骚扰|疯狂|不停|一直打|轰炸'"
new_exp_moderate = "exp_moderate_kw = r'涨了|翻倍|全是|根本|一直|太慢|太复杂|太繁琐|藏得|找不到|不解决|不处理|没人|不理|不管|骗|虚假|陷阱|套路|坑|差|烂|垃圾|恶心|气死|气炸|火大|无语|失望|寒心|过分|离谱|坑爹|坑人|霸王|欺负|歧视|区别对待|不公平|不一致|不一样|差太多|差远了|差很大|天差地别|趁火打劫|坐地起价|乱收费|多收费|重复收费|隐藏费用|强制消费|捆绑销售|诱导消费|虚假促销|虚假优惠|先涨后降|明降暗涨|货不对板|缺斤少两|以次充好|偷工减料|敷衍|推诿|踢皮球|不负责|不作为|不专业|不礼貌|态度恶劣|态度差|骂人|辱骂|威胁|恐吓|骚扰|疯狂|不停|一直打|轰炸|\\d+天|一个月|开不了|看不懂|不灵活|不好用|不完整|不齐全|不全面|不详细|不准确|不靠谱|不放心|不踏实|不安心|不省心|担心|害怕|焦虑|着急|急死了|等不及|等不了|等不起|耗不起|耽误事|误事|坏事|出事|危险|风险|隐患|漏洞|缺陷|毛病|问题多|问题大|问题严重|频繁|经常|总是|老是|动不动|三天两头|隔三差五|没完没了|无休止|无止境|没个头|没完|不停|不断|连续|持续|反复|一再|多次|好几次|无数次|数不清|记不清|麻木|无奈|无力|无助|绝望|崩溃|疯了|受不了|忍不了|忍无可忍|不能再忍|忍到极限|极限|底线|红线|原则|尊严|人格|人权|权益|利益|损失|损害|伤害|受伤|受害|吃亏|上当|被骗|被坑|被宰|被割|被收割|被薅|被薅羊毛|被套路|被算计|被利用|被消费|被浪费|被耽误|被拖累|被连累|被牵连|被影响|被干扰|被打扰|被骚扰|被侵犯|被侵害|被损害|被破坏|被毁|被毁掉|被毁灭|被摧毁|被粉碎|被打破|被打乱|被搞乱|被弄乱|被搅乱|被扰乱|被干扰|被打断|被中断|被终止|被停止|被暂停|被取消|被关闭|被封锁|被屏蔽|被过滤|被审查|被监控|被跟踪|被监视|被监听|被偷窥|被偷看|被偷听|被偷拍|被偷录|被偷窃|被盗取|被盗用|被冒用|被冒充|被伪造|被篡改|被修改|被删除|被移除|被清空|被清零|被归零|被抹去|被抹掉|被擦除|被消除|被消灭|被抹杀|被扼杀|被扼制|被压制|被压抑|被抑制|被限制|被约束|被束缚|被捆绑|被绑架|被挟持|被威胁|被恐吓|被吓唬|被吓到|被吓坏|被吓傻|被吓呆|被吓懵|被吓晕|被吓死|被吓跑|被吓退|被吓走|被吓逃|被吓躲|被吓藏|被吓缩'"

print(f'exp_moderate_kw 旧版: {content.count(old_exp_moderate)} 处')
content = content.replace(old_exp_moderate, new_exp_moderate)
print(f'exp_moderate_kw 新版: {content.count(new_exp_moderate)} 处')

content = content.replace("apply_priority_rules v6.3", "apply_priority_rules v6.4")

with open('SpecMark最新.yml', 'w', encoding='utf-8') as f:
    f.write(content)

try:
    yaml.safe_load(content)
    print('\nYAML 解析: OK')
except Exception as e:
    print(f'\nYAML 解析: FAIL - {e}')

print(f'v6.4 标记: {len(re.findall(r"v6\.4", content))} 处')

# ===== 3. 同步测试脚本 =====
with open('_v6_test.py', 'r', encoding='utf-8') as f:
    test = f.read()

test = test.replace(old_svc_high, new_svc_high)
test = test.replace(old_perf_severe, new_perf_severe)
test = test.replace(old_exp_moderate, new_exp_moderate)
test = test.replace("apply_priority_rules v6.3", "apply_priority_rules v6.4")

with open('_v6_test.py', 'w', encoding='utf-8') as f:
    f.write(test)

print(f'测试脚本 v6.4 标记: {len(re.findall(r"v6\.4", test))} 处')
print('\n✅ v6.4 升级完成')
