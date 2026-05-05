import yaml
import re
import shutil

YAML_PATH = r'd:\产品分析\SpecMark\workflow\SpecMark最新.yml'
BACKUP_PATH = YAML_PATH + '.v5bak'

shutil.copy2(YAML_PATH, BACKUP_PATH)
print(f"Backup: {BACKUP_PATH}")

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

def make_iron_classify_v5():
    return '''def iron_classify(text):
        irony_pos = ['太棒了', '绝了', '真厉害', '厉害了', '完美']
        irony_neg = ['闪退', '崩溃', '死机']
        if any(k in text for k in irony_pos) and any(k in text for k in irony_neg):
            return ('功能', '负向', None)
        neg_ctx = ['但', '但是', '不过', '就是', '可惜', '然而', '只是', '可是', '虽然',
                   '差评', '问题', '气愤', '威胁', '刷', '假', '骗', '坑', '垃圾', '太差',
                   '不满', '投诉', '拒', '不解决', '不管']
        pos_words = ['很好', '好用', '专业', '不错', '很棒', '超好用',
                     '体验很好', '给力', '真香', '效率提高', '帮助提高', '支持导出',
                     '覆盖广', '很全', '很细', '很准', '很及时', '很方便', '很酷',
                     '很震撼', '很到位', '准时送达', '好评']
        if any(k in text for k in pos_words):
            if not any(n in text for n in neg_ctx):
                return ('体验', '正向', '低')
        fixed_signals = ['修好了', '已解决', '已修复', '终于不', '终于没', '恢复正常',
                         '不再闪退', '不再崩溃', '不再报错']
        if any(k in text for k in fixed_signals):
            return None
        has_func_failure = bool(re.search(
            r'闪退|崩溃|死机|白屏|黑屏|变砖|强制退出|ANR|'
            r'支付失败|扣款异常|重复扣款|数据丢失|登录不上|账号被盗|'
            r'隐私泄露|隐私暴露|不明扣款|打不开|一片空白|404|'
            r'功能失效|没反应|报错|上传失败|下载失败|保存失败|'
            r'同步失败|不能用|没法用|用不了|无响应|失效|失灵|'
            r'保存不了|传不了|下不了|载不出|掉线|断连|无法连接|'
            r'连不上|连接失败|断开|验证码收不到|注册失败|被盗|被封|'
            r'被限流|被禁言|数据异常|金额算错|乱码|订单消失|记录没了|'
            r'聊天记录没了|卡死无法|卡死不能|无法跳转|形同虚设|绕过|绕开|'
            r'识别不准|识别率太低|准确率太低|'
            r'被锁|锁了|封禁|解封|申诉|风控|拦截|'
            r'没到账|不到账|钱没到|扣了钱|订单没生成|'
            r'多扣|金额不对|账单不对|'
            r'没声音|播放不了|播放没声音|没声|'
            r'识别不通过|识别失败|'
            r'恢复不了|没恢复|恢复失败|'
            r'定位.{0,2}飘|定位.{0,2}偏|定位不准|定位偏差|'
            r'不见了|消失|丢失|'
            r'被举报|限制转账|限制提现|账户限制|账户冻结|'
            r'不工作|不运行|无法使用|不可用|'
            r'关不掉|取消不了|停不了|'
            r'扣了.{0,4}费|扣了.{0,4}钱|'
            r'找不到了|显示空白|收藏夹空白|'
            r'数据不同步|状态不同步|信息不同步|'
            r'不执行|不生效|功能缺失|'
            r'识别率低|成功率太低|'
            r'误报|漏发|卡粮|'
            r'上不了网|'
            r'突然没了|突然.{0,2}没|'
            r'离线频繁|频繁.*掉线|'
            r'格式不对|出粮不均匀|'
            r'识别不了|不认了|'
            r'不支持|做不到|不能自定义',
            text
        ))
        has_content_issue = bool(re.search(
            r'图文不符|描述不符|实物不符|货不对板|缺斤少两|'
            r'虚假宣传|夸大宣传|误导|标称|标示|'
            r'推荐不准|推荐不好|搜索不对|搜不到|搜出来不对|'
            r'匹配不公|匹配机制|算法有问题|'
            r'翻译错|字幕不同步|歌词延迟|歌词翻译不对|'
            r'内容过时|信息旧|攻略过时|信息过时|'
            r'数据有延迟|数据延迟|不准确|算错|'
            r'答案有错|题库.*错|'
            r'对不上|不准确',
            text
        ))
        exp_surface_keywords = ['退款', '售后', '客服', '骑手', '司机', '商家', '配送',
                                '退货', '换货', '拒赔', '投诉', '举报']
        has_exp_surface = any(k in text for k in exp_surface_keywords)
        exp_override = bool(re.search(
            r'画质|护眼|模式太暗|动画.*挡|挡.*画面|'
            r'更新.*不能用|不能用.*更新|'
            r'流程.*繁琐|繁琐.*审核|流程.*审核|'
            r'看不清',
            text
        ))
        perf_context = bool(re.search(
            r'太慢|很慢|特别慢|等了|等\\d+秒|响应慢|加载慢|启动慢|'
            r'变卡|太卡|很卡|卡顿|帧率|掉帧|不流畅',
            text
        ))
        content_context = bool(re.search(
            r'病历.*不完整|报表.*不准确|数据.*不准确|'
            r'数据.*对不上|销售额.*对不上|续航.*虚标|能耗.*不准|'
            r'翻译错|术语.*翻译|'
            r'虚标|标称.*不符|显示.*不准',
            text
        ))
        func_connection = bool(re.search(
            r'蓝牙.*连接|连接.*蓝牙|蓝牙.*断|断.*蓝牙|'
            r'蓝牙.*卡|卡.*蓝牙|蓝牙.*延迟',
            text
        ))
        func_device_stuck = bool(re.search(
            r'卡住.*不动|卡住不动|转了.*卡住|卡住$',
            text
        ))
        if has_func_failure and has_exp_surface:
            func_high_kw = ['支付', '扣款', '订单', '账号', '登录', '数据', '账单',
                            '同步失败', '丢失', '消失', '被盗', '被封', '封禁', '锁了',
                            '风控', '转账', '到账', '隐私', '泄露', '报错', '失败',
                            '闪退', '崩溃', '死机', '白屏', '黑屏', '打不开', '用不了',
                            '不能用', '没法用', '连不上', '掉线', '断连', '没反应',
                            '被锁', '拦截', '限制', '冻结', '多扣', '对不上', '没到账',
                            '关不掉', '取消不了', '扣了', '不执行', '不生效', '丢失']
            if any(k in text for k in func_high_kw):
                return ('功能', '负向', None)
            return ('功能', '负向', None)
        if has_func_failure and not has_content_issue and not exp_override and not perf_context:
            if content_context:
                return ('内容', '负向', None)
            return ('功能', '负向', None)
        if has_func_failure and perf_context and not has_content_issue and not exp_override:
            if re.search(r'太慢.*用不了|用不了.*太慢|等\\d+秒.*用不了|用不了.*等', text):
                return ('性能', '负向', None)
            return ('功能', '负向', None)
        if func_connection:
            return ('功能', '负向', None)
        if func_device_stuck:
            return ('功能', '负向', None)
        if content_context and not has_func_failure:
            return ('内容', '负向', None)
        if has_content_issue and has_exp_surface:
            content_high_kw = ['不符', '虚假', '夸大', '误导', '缺斤少两', '货不对板']
            if any(k in text for k in content_high_kw):
                return ('内容', '负向', None)
            return ('内容', '负向', None)
        func_rules = [
            (['闪退', '崩溃', '死机', '白屏', '黑屏', '变砖', '强制退出', 'ANR'], '功能', '负向'),
            (['支付失败', '扣款异常', '重复扣款', '数据丢失', '登录不上', '账号被盗',
              '隐私泄露', '隐私暴露', '不明扣款'], '功能', '负向'),
            (['打不开', '一片空白', '404', '功能失效', '没反应', '报错',
              '上传失败', '下载失败', '保存失败', '同步失败',
              '不能用', '没法用', '用不了', '无响应', '失效', '失灵',
              '保存不了', '传不了', '下不了', '载不出'], '功能', '负向'),
            (['掉线', '断连', '无法连接', '连不上', '连接失败', '断开'], '功能', '负向'),
            (['验证码收不到', '注册失败'], '功能', '负向'),
            (['被盗', '被封', '被限流', '被禁言'], '功能', '负向'),
            (['数据异常', '金额算错', '乱码', '订单消失', '记录没了', '聊天记录没了'], '功能', '负向'),
            (['卡死无法', '卡死不能', '无法跳转'], '功能', '负向'),
            (['形同虚设', '绕过', '绕开'], '功能', '负向'),
            (['识别不准', '识别率太低', '准确率太低'], '功能', '负向'),
            (['被锁', '封禁', '风控', '拦截'], '功能', '负向'),
            (['没到账', '不到账', '多扣'], '功能', '负向'),
            (['没声音', '播放不了', '播放没声音'], '功能', '负向'),
            (['恢复不了', '恢复失败'], '功能', '负向'),
            (['账户限制', '账户冻结', '限制转账', '限制提现'], '功能', '负向'),
        ]
        svc_rules = [
            (['配送超时', '配送慢', '餐品凉', '洒了', '扔门口', '送餐慢',
              '骑手态度', '司机态度', '骑手恶劣', '司机绕路', '提前确认送达'], '体验', '负向'),
            (['吃出异物', '食物变质', '食品安全', '餐品变质', '寄生虫'], '体验', '负向'),
            (['商家取消', '商家不承认', '商家不管', '拒赔', '拒不赔偿',
              '拒绝退款', '拒绝理赔'], '体验', '负向'),
            (['自动续费', '大数据杀熟', '杀熟'], '体验', '负向'),
            (['客服不管', '客服不解决', '客服推诿', '客服机器人', '客服打不通',
              '客服态度', '模板话术', '没人处理', '推诿责任', '不作为'], '体验', '负向'),
            (['退款慢', '售后慢', '审核太慢', '退款等了', '售后审核'], '体验', '负向'),
            (['臭车', '卫生环境', '异味', '车内异味'], '体验', '负向'),
            (['不安全驾驶', '安全隐患'], '体验', '负向'),
        ]
        perf_rules = [
            (['卡顿', '太卡了', '很卡', '变卡', '不流畅',
              '卡得', '卡的要死', '卡死了', '卡的要命'], '性能', '负向'),
            (['加载慢', '启动慢', '打开慢', '响应慢', '运行慢',
              '限速', '上传限速'], '性能', '负向'),
            (['延迟高', '网络延迟', '高延迟', '延迟太大', '延迟严重'], '性能', '负向'),
            (['耗电', '费电', '掉电快', '发烫', '过热',
              '续航虚标', '续航差', '电池掉电'], '性能', '负向'),
            (['掉帧', '帧率低', '不跟手', '画面不流畅'], '性能', '负向'),
            (['缓冲', '转圈圈', '一直转圈', 'loading', '缓冲中', '转半天'], '性能', '负向'),
            (['占用高', '内存高', '资源占用', '假死', 'CPU高',
              '占用太大', '占用太多', '包太大', '安装包大', '更新包大'], '性能', '负向'),
            (['画面延迟', '声音延迟', '画面不同步', '声音不同步'], '性能', '负向'),
        ]
        content_rules = [
            (['推荐不准', '推荐不好', '推荐单一', '推荐重复', '推荐过时',
              '推荐越来越', '同质化'], '内容', '负向'),
            (['搜索不对', '搜不到', '搜出来不对', '搜索结果不相关',
              '版权覆盖太少'], '内容', '负向'),
            (['匹配不公', '匹配机制', '算法有问题', '算法推荐'], '内容', '负向'),
            (['翻译错', '字幕不同步', '歌词延迟', '歌词翻译不对'], '内容', '负向'),
            (['图文不符', '描述不符', '实物不符', '刷评', '水军',
              '内容过时', '信息旧', '攻略过时', '信息过时'], '内容', '负向'),
            (['黄色', '暧昧信息', '低俗', '戾气'], '内容', '负向'),
            (['数据有延迟', '数据延迟'], '内容', '负向'),
            (['虚假宣传', '夸大宣传', '缺斤少两', '货不对板'], '内容', '负向'),
        ]
        suggest_rules = [
            (['能不能', '希望', '建议', '想要', '加个', '能不能加'], '体验', '中性'),
        ]
        other_exp_rules = [
            (['广告', '推送太多', '操作复杂', '找不到入口', '太贵', '涨价',
              '诱导', '套路', '权益缩水', 'VIP专属', '免费用户', '吃相'], '体验', '负向'),
            (['太麻烦', '繁琐', '找不到', '难找', '不方便', '不好用',
              '难用', '步骤太多', '设置太深', '隐藏得太深', '太复杂'], '体验', '负向'),
            (['预售', '发货时间', '没发货', '物流', '发货'], '体验', '负向'),
            (['配送费'], '体验', '负向'),
        ]
        all_rules = func_rules + svc_rules + perf_rules + content_rules + suggest_rules + other_exp_rules
        if re.search(r'流程.*繁琐|流程.*审核|繁琐.*审核', text):
            if re.search(r'审核不通过|审核拒绝', text):
                return ('体验', '负向', None)
        if re.search(r'更新.*不能用|更新.*用不了|不能用.*更新|用不了.*更新', text):
            return ('体验', '负向', None)
        if re.search(r'动画.*挡|挡.*画面', text):
            if re.search(r'关不掉|看不清', text):
                return ('体验', '负向', None)
        if re.search(r'课程.*更新|更新.*课程|教材.*换', text):
            if re.search(r'太慢|还是旧|没更新', text):
                return ('体验', '负向', None)
        if re.search(r'搜索.*找不到|搜.*不相关', text):
            if not has_func_failure and not re.search(r'广告|推广|付费', text):
                return ('内容', '负向', None)
        if re.search(r'材质.*不一样|详情.*写.*收到', text):
            return ('内容', '负向', None)
        for keywords, ptype, sentiment in all_rules:
            if any(k in text for k in keywords):
                return (ptype, sentiment, None)
        if re.search(r'(?:太|很|特别|变|更|越|也|都|还是|就是).*卡|卡(?:顿|住|得|的|了)', text):
            if not re.search(r'银行卡|打卡|会员卡|卡通|卡片|卡包', text):
                return ('性能', '负向', None)
        if re.search(r'(?:太|很|特别|更|越).*慢|慢(?:了|得|的)', text):
            if not re.search(r'回复.*慢|问诊|医生|客服.*慢|退款|售后|审核|物流|发货|配送', text):
                return ('性能', '负向', None)
        if re.search(r'启动.{0,3}\\d+秒|启动要|打开要', text):
            return ('性能', '负向', None)
        if '续航' in text:
            return ('性能', '负向', None)
        if '假死' in text:
            return ('性能', '负向', None)
        if '限速' in text:
            return ('性能', '负向', None)
        if re.search(r'(?:资源|内存|CPU).*(?:占用|高|大|太多)', text):
            return ('性能', '负向', None)
        if re.search(r'转.{0,3}圈', text):
            if not re.search(r'朋友圈|社交圈', text):
                return ('性能', '负向', None)
        if re.search(r'手机.{0,3}烫|烫.{0,3}手', text):
            return ('性能', '负向', None)
        if re.search(r'延迟.{0,4}(?:大|严重|高|太多)', text):
            if not re.search(r'数据.*延迟|汇率.*延迟|牌价.*延迟', text):
                return ('性能', '负向', None)
        if re.search(r'不同步', text):
            if re.search(r'数据|状态|信息|订单|库存|记录', text):
                return ('功能', '负向', None)
            if not re.search(r'字幕|歌词|翻译', text):
                return ('性能', '负向', None)
        if re.search(r'数据.{0,2}延迟|汇率.*延迟|牌价.*延迟', text):
            return ('内容', '负向', None)
        if '描述不符' in text or '实物不符' in text or '缺斤少两' in text:
            return ('内容', '负向', None)
        if re.search(r'刷.{0,1}评|假评|水军|五星好评', text):
            return ('内容', '负向', None)
        if '杀熟' in text:
            return ('体验', '负向', None)
        if re.search(r'关不掉|取消不了|停不了', text):
            if exp_override:
                return ('体验', '负向', None)
            return ('功能', '负向', None)
        if re.search(r'审核不通过|审核.*拒绝', text):
            if re.search(r'流程|繁琐', text):
                return ('体验', '负向', None)
            return ('功能', '负向', None)
        if re.search(r'不能用|用不了|没法用', text):
            if re.search(r'更新|升级', text):
                return ('体验', '负向', None)
            if perf_context:
                return ('性能', '负向', None)
            if re.search(r'根本用不了|多了.*用不了', text):
                if re.search(r'太慢|很慢|等\\d+秒', text):
                    return ('性能', '负向', None)
            return ('功能', '负向', None)
        if re.search(r'对不上', text):
            if re.search(r'数据|报表|销售额|财务|账', text):
                return ('内容', '负向', None)
            return ('功能', '负向', None)
        if re.search(r'不完整', text):
            if re.search(r'病历|检查结果|病历记录', text):
                return ('内容', '负向', None)
            return ('功能', '负向', None)
        if re.search(r'退款|售后|退货|换货|拒赔', text):
            return ('体验', '负向', None)
        if re.search(r'配送|骑手|司机|打车|叫车|网约车|顺风车|拼车|接单|接机', text):
            return ('体验', '负向', None)
        if '客服' in text:
            return ('体验', '负向', None)
        if re.search(r'广告|推送|弹窗|开屏', text):
            return ('体验', '负向', None)
        if re.search(r'太贵|涨价|价格|不值|性价比|抽奖|充更多', text):
            return ('体验', '负向', None)
        if re.search(r'会员|VIP|付费|充值|续费|红包|权益', text):
            return ('体验', '负向', None)
        if re.search(r'能不能|希望|建议|想要|加个', text):
            return ('体验', '中性', None)
        if re.search(r'找不到|复杂|麻烦|繁琐|难找|不方便|设置太深|隐私设置', text):
            return ('体验', '负向', None)
        if re.search(r'定位不准|定位偏差', text):
            return ('功能', '负向', None)
        if re.search(r'照片被压缩|画质.*变|压缩.*模糊', text):
            return ('功能', '负向', None)
        if re.search(r'折叠|翻半天', text):
            return ('体验', '负向', None)
        if '无法撤回' in text:
            return ('功能', '负向', None)
        if re.search(r'账户.{0,2}限制|账户.{0,2}冻结|限制.*转账|限制.*提现', text):
            return ('功能', '负向', None)
        if re.search(r'额度太低|额度不够', text):
            return ('体验', '负向', None)
        if re.search(r'到店.*没房|预订.*没房|没房了', text):
            return ('体验', '负向', None)
        if re.search(r'没人接单|没接单', text):
            return ('体验', '负向', None)
        if re.search(r'次日达|等了\\d+天|等了\\d+分钟', text):
            return ('体验', '负向', None)
        if re.search(r'信息过时|早就关门|攻略.*过时', text):
            return ('内容', '负向', None)
        if re.search(r'规则不透明|不透明', text):
            return ('体验', '负向', None)
        if re.search(r'威胁|骚扰|疯狂打电话', text):
            return ('体验', '负向', None)
        if re.search(r'重影|竖条|刮痕|显示屏', text):
            return ('体验', '负向', None)
        if re.search(r'运费|退货.*运费', text):
            return ('体验', '负向', None)
        if re.search(r'材质.*不符|手感.*不一样', text):
            return ('内容', '负向', None)
        if re.search(r'功能臃肿|臃肿|花里胡哨', text):
            return ('体验', '负向', None)
        if re.search(r'bug|Bug|BUG', text):
            return ('功能', '负向', None)
        if re.search(r'崩了|大面积故障|服务异常', text):
            return ('功能', '负向', None)
        if re.search(r'识别为外出|打卡.*迟到|打卡.*外勤', text):
            return ('功能', '负向', None)
        if re.search(r'付费推广|前五页', text):
            return ('体验', '负向', None)
        if re.search(r'已读回执|已读', text):
            return ('体验', '中性', None)
        return None'''

nodes = data['workflow']['graph']['nodes']
modified = 0

for node in nodes:
    nd = node.get('data', {})
    if nd.get('type') != 'code' or 'code' not in nd:
        continue
    code = nd['code']
    if 'iron_classify' not in code:
        continue

    title = nd.get('title', 'unknown')
    print(f"\nProcessing: {title}")

    # 1. Replace iron_classify function
    old_func_match = re.search(r'def iron_classify\(text\):.*?return None\n', code, re.DOTALL)
    if not old_func_match:
        old_func_match = re.search(r'def iron_classify\(text\):.*?return None$', code, re.DOTALL)
    if old_func_match:
        new_func = make_iron_classify_v5()
        code = code[:old_func_match.start()] + new_func + code[old_func_match.end():]
        print(f"  Replaced iron_classify function")
    else:
        print(f"  WARNING: Could not find iron_classify function")
        continue

    # 2. Replace result handler for single-feedback nodes (Node 12, 15)
    # Old: result = iron_classify(text)\n    if result:\n        ptype, sentiment,priority = result\n        source = '铁律拦截'
    # New: result = iron_classify(text)\n    if result:\n        ptype, sentiment, iron_priority = result\n        source = '铁律拦截'
    old_handler = re.search(
        r"result\s*=\s*iron_classify\(text\)\s+if\s+result:\s+ptype,\s*sentiment\s*,\s*priority\s*=\s*result\s+source\s*=\s*'铁律拦截'",
        code
    )
    if old_handler:
        new_handler = "result = iron_classify(text)\n    if result:\n        ptype, sentiment, iron_priority = result\n        source = '铁律拦截'"
        code = code[:old_handler.start()] + new_handler + code[old_handler.end():]
        print(f"  Replaced result handler (single-feedback)")
    else:
        # Check for batch handler
        old_batch_handler = re.search(
            r"result\s*=\s*iron_classify\(feedback_text\)\s+if\s+result:\s+ptype,\s*sentiment,\s*priority\s*=\s*result",
            code
        )
        if old_batch_handler:
            new_batch_handler = "result = iron_classify(feedback_text)\n        if result:\n            ptype, sentiment, iron_priority = result"
            code = code[:old_batch_handler.start()] + new_batch_handler + code[old_batch_handler.end():]
            print(f"  Replaced result handler (batch)")
        else:
            print(f"  WARNING: Could not find result handler")

    # 3. Replace priority handler for single-feedback nodes
    # Old: priority = llm_result.get('priority', '低')\n            if prioritynot in ['高', '中', '低']:\n                priority = '低'
    # New: if iron_priority is not None:\n                priority = iron_priority\n            else:\n                priority = llm_result.get('priority', '低')\n                if priority not in ['高', '中', '低']:\n                    priority = '低'
    old_prio = re.search(
        r"priority\s*=\s*llm_result\.get\('priority',\s*'低'\)\s+if\s+prioritynot\s+in\s+\['高',\s*'中',\s*'低'\]:\s+priority\s*=\s*'低'",
        code
    )
    if old_prio:
        new_prio = "if iron_priority is not None:\n                priority = iron_priority\n            else:\n                priority = llm_result.get('priority', '低')\n                if priority not in ['高', '中', '低']:\n                    priority = '低'"
        code = code[:old_prio.start()] + new_prio + code[old_prio.end():]
        print(f"  Replaced priority handler (single-feedback)")
    else:
        # Check for batch priority handler
        # In batch mode, after ptype, sentiment, iron_priority = result
        # We need to add: if iron_priority is not None: priority = iron_priority else: priority = '低'
        # But batch mode doesn't have LLM fallback, so just set priority from iron_priority
        batch_prio = re.search(
            r"ptype, sentiment, iron_priority = result\s+else:\s+ptype\s*=\s*'体验'\s+sentiment\s*=\s*'中性'\s+priority\s*=\s*'低'",
            code
        )
        if batch_prio:
            new_batch_prio = "ptype, sentiment, iron_priority = result\n            priority = iron_priority if iron_priority is not None else '低'\n        else:\n            ptype = '体验'\n            sentiment = '中性'\n            priority = '低'"
            code = code[:batch_prio.start()] + new_batch_prio + code[batch_prio.end():]
            print(f"  Replaced priority handler (batch)")
        else:
            print(f"  WARNING: Could not find priority handler")

    nd['code'] = code
    modified += 1

print(f"\nModified {modified} code nodes")

class PreserveStr(str):
    pass

def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_representer)

with open(YAML_PATH, 'w', encoding='utf-8') as f:
    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("YAML written. Validating...")

with open(YAML_PATH, 'r', encoding='utf-8') as f:
    test_data = yaml.safe_load(f)

test_nodes = test_data['workflow']['graph']['nodes']
for node in test_nodes:
    nd = node.get('data', {})
    if nd.get('type') == 'code' and 'code' in nd:
        code = nd['code']
        if 'iron_classify' in code:
            has_none = "return ('功能', '负向', None)" in code
            has_iron_priority = 'iron_priority' in code
            print(f"  {nd.get('title', '?')}: has_none_priority={has_none}, has_iron_priority={has_iron_priority}")

print("\nDone!")
