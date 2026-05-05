import csv
import re

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

def iron_classify_v6(text):
    # iron_classify v6.1 2026-04-29
    # Priority rules aligned with knowledge base v6.0 priority matrix

    # --- Priority keyword sets ---
    func_high_kw = r'闪退|崩溃|死机|白屏|黑屏|变砖|支付失败|数据丢失|登录不上|账号被盗|隐私泄露'
    svc_high_kw = r'食品安全|异物|变质|寄生虫|吃出|拉肚子|食物中毒|发霉|馊了|臭了|不新鲜|拒赔|骑手态度|司机态度|等超久|自动续费|被欺骗|等了\d+分钟|等了\d+小时|没人接单|没接单|骚扰|威胁'
    perf_high_kw = r'发烫|不敢用|完全卡死|卡死'
    content_high_kw = r'虚假宣传|诈骗|假货|杀熟|刷.{0,1}评|假评|水军'

    # === Step 1: Irony & Positive ===
    irony_pos = ['太棒了', '绝了', '真厉害', '厉害了', '完美']
    irony_neg = ['闪退', '崩溃', '死机']
    if any(k in text for k in irony_pos) and any(k in text for k in irony_neg):
        return ('功能', '负向', '高')

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

    # === Step 2: Suggest → 体验 ===
    if re.search(r'能不能|希望|建议|想要|加个|能不能加', text):
        return ('体验', '中性', '低')

    # === Step 3: Detect signals ===
    true_crash = bool(re.search(
        r'闪退|崩溃|死机|白屏|黑屏|变砖|强制退出|ANR|'
        r'支付失败|扣款异常|重复扣款|数据丢失|登录不上|账号被盗|'
        r'隐私泄露|隐私暴露|不明扣款|'
        r'打不开|一片空白|404|'
        r'同步失败|数据异常|金额算错|乱码|订单消失|记录没了|聊天记录没了|'
        r'验证码收不到|注册失败|'
        r'被盗|被封|被限流|被禁言|被锁|封禁|风控|拦截|'
        r'没到账|不到账|钱没到|扣了钱|订单没生成|多扣|金额不对|账单不对|'
        r'账户限制|账户冻结|限制转账|限制提现|'
        r'没声音|播放不了|播放没声音|'
        r'恢复不了|恢复失败|'
        r'数据不同步|状态不同步|信息不同步|'
        r'升级失败|识别不了',
        text
    ))

    broad_func_failure = bool(re.search(
        r'闪退|崩溃|死机|白屏|黑屏|变砖|强制退出|ANR|'
        r'支付失败|扣款异常|重复扣款|数据丢失|登录不上|账号被盗|'
        r'隐私泄露|隐私暴露|不明扣款|'
        r'打不开|一片空白|404|'
        r'功能失效|没反应|报错|'
        r'上传失败|下载失败|保存失败|同步失败|'
        r'不能用|没法用|用不了|无响应|失效|失灵|'
        r'保存不了|传不了|下不了|载不出|'
        r'掉线|断连|无法连接|连不上|连接失败|断开|'
        r'验证码收不到|注册失败|'
        r'被盗|被封|被限流|被禁言|'
        r'数据异常|金额算错|乱码|订单消失|记录没了|聊天记录没了|'
        r'卡死无法|卡死不能|无法跳转|形同虚设|绕过|绕开|'
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
        r'不支持|做不到|不能自定义|'
        r'识别不准|识别率太低|准确率太低|'
        r'升级失败|变砖',
        text
    ))

    # === Step 4: Service/Delivery → 体验 ===
    pure_svc = ['骑手', '配送', '商家', '餐品', '食物', '外卖', '快递', '驿站', '快递柜', '包裹', '取件码', '送餐']
    has_pure_svc = any(k in text for k in pure_svc)
    ambig_svc = ['退款', '售后', '客服', '退货', '换货', '拒赔', '投诉', '举报', '物流', '发货', '报修', '物业', '保洁']
    has_ambig_svc = any(k in text for k in ambig_svc)
    has_driver = '司机' in text

    # Pure service + func failure → 体验 (except 定位)
    if has_pure_svc and broad_func_failure:
        if re.search(r'定位.{0,2}飘|定位.{0,2}偏|定位不准|定位偏差', text):
            p = '高' if re.search(func_high_kw, text) else '中'
            return ('功能', '负向', p)
        p = '高' if re.search(svc_high_kw, text) else '低'
        return ('体验', '负向', p)

    if has_pure_svc and not broad_func_failure:
        p = '高' if re.search(svc_high_kw, text) else '低'
        return ('体验', '负向', p)

    # Driver + func failure
    if has_driver and broad_func_failure:
        if re.search(r'扣了|扣费|取消费|扣款|多扣|不到账|没到账', text):
            p = '高' if re.search(func_high_kw, text) else '中'
            return ('功能', '负向', p)
        if re.search(r'定位.{0,2}飘|定位.{0,2}偏|定位不准|定位偏差', text):
            p = '高' if re.search(func_high_kw, text) else '中'
            return ('功能', '负向', p)
        p = '高' if re.search(svc_high_kw, text) else '低'
        return ('体验', '负向', p)

    if has_driver and not broad_func_failure:
        p = '高' if re.search(svc_high_kw, text) else '低'
        return ('体验', '负向', p)

    # Ambiguous svc + true crash → 功能
    if has_ambig_svc and true_crash:
        p = '高' if re.search(func_high_kw, text) else '中'
        return ('功能', '负向', p)

    # Ambiguous svc + broad func failure
    if has_ambig_svc and broad_func_failure:
        strong_func_signals = bool(re.search(
            r'扣了钱|订单没生成|没到账|不到账|钱没到|多扣|金额不对|账单不对|'
            r'格式不对|变砖|升级失败|'
            r'数据异常|金额算错|乱码|订单消失|记录没了|'
            r'被锁|封禁|风控|拦截|账户限制|账户冻结|'
            r'打不开|一片空白|404|'
            r'识别不了|识别不通过',
            text
        ))
        if strong_func_signals:
            p = '高' if re.search(func_high_kw, text) else '中'
            return ('功能', '负向', p)
        p = '低'
        return ('体验', '负向', p)

    # === Step 5: Pure func failure → 功能 ===
    if broad_func_failure:
        has_perf = bool(re.search(
            r'卡顿|太卡了|很卡|变卡|不流畅|卡得|卡的要死|卡死了|卡的要命|'
            r'加载慢|启动慢|打开慢|响应慢|运行慢|'
            r'延迟高|网络延迟|高延迟|延迟太大|延迟严重|'
            r'耗电|费电|掉电快|发烫|过热|'
            r'掉帧|帧率低|不跟手|画面不流畅|'
            r'缓冲|转圈圈|一直转圈|loading|缓冲中|'
            r'占用高|内存高|资源占用|CPU高|'
            r'画面延迟|声音延迟|画面不同步|声音不同步',
            text
        ))
        if has_perf:
            if re.search(r'太慢.*用不了|用不了.*太慢|等\d+秒.*用不了|用不了.*等', text):
                p = '高' if re.search(perf_high_kw, text) else '中'
                return ('性能', '负向', p)
        p = '高' if re.search(func_high_kw, text) else '中'
        return ('功能', '负向', p)

    # === Step 6: Performance → 性能 ===
    if re.search(r'(?:太|很|特别|变|更|越|也|都|还是|就是).*卡|卡(?:顿|住|得|的|了)', text):
        if not re.search(r'银行卡|打卡|会员卡|卡通|卡片|卡包', text):
            p = '高' if re.search(perf_high_kw, text) else '中'
            return ('性能', '负向', p)
    if re.search(r'(?:太|很|特别|更|越).*慢|慢(?:了|得|的)', text):
        if not re.search(r'回复.*慢|问诊|医生|客服.*慢|退款|售后|审核|物流|发货|配送', text):
            p = '高' if re.search(perf_high_kw, text) else '中'
            return ('性能', '负向', p)
    if re.search(r'启动.{0,3}\d+秒|启动要|打开要', text):
        return ('性能', '负向', '中')
    if '续航' in text:
        return ('性能', '负向', '中')
    if '假死' in text:
        return ('性能', '负向', '高')
    if '限速' in text:
        return ('性能', '负向', '中')
    if re.search(r'(?:资源|内存|CPU).*(?:占用|高|大|太多)', text):
        return ('性能', '负向', '中')
    if re.search(r'转.{0,3}圈', text):
        if not re.search(r'朋友圈|社交圈', text):
            return ('性能', '负向', '中')
    if re.search(r'手机.{0,3}烫|烫.{0,3}手', text):
        return ('性能', '负向', '高')
    if re.search(r'延迟.{0,4}(?:大|严重|高|太多)', text):
        if not re.search(r'数据.*延迟|汇率.*延迟|牌价.*延迟', text):
            return ('性能', '负向', '中')
    if re.search(r'不同步', text):
        if re.search(r'数据|状态|信息|订单|库存|记录', text):
            p = '高' if re.search(func_high_kw, text) else '中'
            return ('功能', '负向', p)
        if not re.search(r'字幕|歌词|翻译', text):
            return ('性能', '负向', '中')

    # === Step 7: Content quality → 内容 ===
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

    if has_content_issue:
        p = '高' if re.search(content_high_kw, text) else '低'
        return ('内容', '负向', p)

    if re.search(r'数据.{0,2}延迟|汇率.*延迟|牌价.*延迟', text):
        return ('内容', '负向', '低')
    if '描述不符' in text or '实物不符' in text or '缺斤少两' in text:
        p = '高' if re.search(content_high_kw, text) else '低'
        return ('内容', '负向', p)
    if re.search(r'刷.{0,1}评|假评|水军|五星好评', text):
        return ('内容', '负向', '高')
    if re.search(r'信息过时|早就关门|攻略.*过时', text):
        return ('内容', '负向', '低')
    if re.search(r'材质.*不符|手感.*不一样', text):
        return ('内容', '负向', '低')

    # === Step 8: Other experience fallbacks ===
    if '杀熟' in text:
        return ('体验', '负向', '高')
    if re.search(r'关不掉|取消不了|停不了', text):
        return ('功能', '负向', '中')
    if re.search(r'审核不通过|审核.*拒绝', text):
        if re.search(r'流程|繁琐', text):
            return ('体验', '负向', '低')
        return ('功能', '负向', '中')
    if re.search(r'不能用|用不了|没法用', text):
        if re.search(r'更新|升级', text):
            return ('体验', '负向', '低')
        p = '高' if re.search(func_high_kw, text) else '中'
        return ('功能', '负向', p)
    if re.search(r'对不上', text):
        if re.search(r'数据|报表|销售额|财务|账', text):
            return ('内容', '负向', '低')
        return ('功能', '负向', '中')
    if re.search(r'不完整', text):
        if re.search(r'病历|检查结果|病历记录', text):
            return ('内容', '负向', '低')
        return ('功能', '负向', '中')
    if re.search(r'退款|售后|退货|换货|拒赔', text):
        p = '高' if '拒赔' in text else '低'
        return ('体验', '负向', p)
    if re.search(r'配送|骑手|司机|打车|叫车|网约车|顺风车|拼车|接单|接机', text):
        p = '高' if re.search(svc_high_kw, text) else '低'
        return ('体验', '负向', p)
    if '客服' in text:
        return ('体验', '负向', '低')
    if re.search(r'广告|推送|弹窗|开屏', text):
        return ('体验', '负向', '低')
    if re.search(r'太贵|涨价|价格|不值|性价比|抽奖|充更多', text):
        return ('体验', '负向', '低')
    if re.search(r'会员|VIP|付费|充值|续费|红包|权益', text):
        p = '高' if re.search(r'自动续费|被欺骗|骗', text) else '低'
        return ('体验', '负向', p)
    if re.search(r'找不到|复杂|麻烦|繁琐|难找|不方便|设置太深|隐私设置', text):
        return ('体验', '负向', '低')
    if re.search(r'定位不准|定位偏差', text):
        return ('功能', '负向', '中')
    if re.search(r'照片被压缩|画质.*变|压缩.*模糊', text):
        return ('功能', '负向', '中')
    if re.search(r'折叠|翻半天', text):
        return ('体验', '负向', '低')
    if '无法撤回' in text:
        return ('功能', '负向', '中')
    if re.search(r'账户.{0,2}限制|账户.{0,2}冻结|限制.*转账|限制.*提现', text):
        return ('功能', '负向', '高')
    if re.search(r'额度太低|额度不够', text):
        return ('体验', '负向', '低')
    if re.search(r'到店.*没房|预订.*没房|没房了', text):
        return ('体验', '负向', '低')
    if re.search(r'没人接单|没接单', text):
        return ('体验', '负向', '高')
    if re.search(r'次日达|等了\d+天|等了\d+分钟', text):
        return ('体验', '负向', '高')
    if re.search(r'规则不透明|不透明', text):
        return ('体验', '负向', '低')
    if re.search(r'威胁|骚扰|疯狂打电话', text):
        return ('体验', '负向', '高')
    if re.search(r'重影|竖条|刮痕|显示屏', text):
        return ('体验', '负向', '低')
    if re.search(r'运费|退货.*运费', text):
        return ('体验', '负向', '低')
    if re.search(r'功能臃肿|臃肿|花里胡哨', text):
        return ('体验', '负向', '低')
    if re.search(r'bug|Bug|BUG', text):
        return ('功能', '负向', '中')
    if re.search(r'崩了|大面积故障|服务异常', text):
        return ('功能', '负向', '高')
    if re.search(r'识别为外出|打卡.*迟到|打卡.*外勤', text):
        return ('功能', '负向', '中')
    if re.search(r'付费推广|前五页', text):
        return ('体验', '负向', '低')
    if re.search(r'已读回执|已读', text):
        return ('体验', '中性', '低')

    return None


def apply_priority_rules(text, ptype, priority):
    # apply_priority_rules v6.4 2026-05-05
    # KB v6.0 Section 四: mitigation downgrade + severity boost + core function boost
    mitigation_kw = r'偶尔|有时|不影响使用|但整体|但基本|还行|勉强|凑合|一般般|还能用|将就|忍了|可以接受'
    no_downgrade_kw = r'闪退|崩溃|死机|数据丢失|支付失败|安全漏洞|食品安全|异物|变质|被欺骗|自动续费|虚假宣传|严重|根本|完全|一直|突然|受不了|忍不了|急用|关键|全错过|没法用|没法玩|没法看|靠不住|来不及'
    if re.search(mitigation_kw, text) and not re.search(no_downgrade_kw, text):
        if priority == '高':
            priority = '中'
        elif priority == '中':
            priority = '低'
    if ptype == '性能' and priority == '中':
        perf_severe_kw = r'严重|根本|完全|一直|突然|太慢|太卡|太大|太短|太严重|很严重|没法|不敢|靠不住|错过|来不及|没法用|没法玩|没法看|受不了|忍不了|急用|关键|全错过|全没了|耽误|废了|毁了|完蛋|崩溃边缘|用不下去|没法工作|没法学习|影响工作|影响学习|断断续续|越来越差|越来越慢|越来越卡|不同步|对不上|等不起|等不了|等不及|太可怕|太吓人|太离谱|太夸张|太差了|太烂了|太垃圾|太恶心|太烦人|太讨厌|太糟糕|太差劲'
        if re.search(perf_severe_kw, text):
            priority = '高'
    if ptype == '功能' and priority == '中':
        core_func_kw = r'支付|登录|下单|订单|转账|账户|交易|充值|提现|扣款|付款|退款|到账|余额|账单|注册|认证|安全|隐私|数据|同步|备份|导出|播放|上传|下载|发送|接收|消息|通知|会员|订阅|续费|匹配|导航|定位|预订|叫车|打车|挂号|问诊|处方|搜索|收藏|评论|分享|点赞|关注|直播|视频|语音|通话|打卡|签到|积分|优惠券|红包|取消|路线|行程|配送|物流|发货|收货|库存|售后|客服|菜单|购物车|商品|秒杀|抽卡|存档|联机|组队|更新|升级|安装|卸载|绑定|解绑|实名|验证|密码|短信|邮箱|手机|人脸|指纹|识别|验证码|注册|注销|激活|开通|关闭|暂停|恢复|重置|修改|变更|迁移|导入|导出|备份|还原|同步|合并|拆分|排序|筛选|过滤|分类|标签|标记|收藏|点赞|评论|回复|转发|分享|举报|投诉|反馈|建议|意见|评价|评分|打分|投票|问卷|调查|调研|测试|试用|体验|预览|演示|展示|推荐|推送|通知|提醒|消息|私信|聊天|对话|会话|通话|视频|语音|直播|播放|暂停|停止|快进|快退|跳过|循环|随机|顺序|列表|歌单|专辑|歌手|歌曲|音乐|音频|声音|音量|音质|音效|均衡|歌词|字幕|翻译|配音|解说|讲解|教程|课程|学习|培训|教育|考试|测验|作业|任务|项目|计划|日程|日历|时间|日期|提醒|闹钟|计时|倒计|秒表|计算|换算|汇率|单位|长度|重量|温度|天气|地图|导航|路线|交通|公交|地铁|火车|飞机|酒店|民宿|景点|门票|攻略|游记|签证|护照|保险|医疗|健康|运动|健身|跑步|骑行|游泳|瑜伽|冥想|睡眠|饮食|营养|食谱|菜谱|烹饪|烘焙|甜点|饮品|咖啡|茶|酒|饮料|水果|蔬菜|肉类|海鲜|零食|小吃|外卖|配送|快递|物流|包裹|邮件|短信|电话|通讯|联系|地址|位置|坐标|经纬|海拔|高度|深度|距离|面积|体积|重量|温度|湿度|气压|风速|风向|降水|天气|气候|环境|生态|自然|动物|植物|生物|化学|物理|数学|统计|概率|逻辑|推理|判断|决策|选择|优化|改进|提升|增强|强化|学习|训练|练习|复习|预习|准备|计划|安排|组织|管理|领导|指挥|协调|沟通|交流|合作|协作|团队|小组|部门|公司|企业|组织|机构|单位|学校|医院|银行|政府|军队|警察|消防|急救|救援|应急|危机|风险|安全|保护|防护|防御|攻击|入侵|病毒|木马|蠕虫|间谍|黑客|破解|盗版|侵权|抄袭|剽窃|伪造|假冒|欺诈|诈骗|欺骗|误导|虚假|不实|谣言|传言|传闻|消息|新闻|资讯|信息|数据|资料|文件|文档|报告|报表|图表|图形|图像|图片|照片|视频|音频|音乐|歌曲|电影|电视|节目|频道|电台|广播|直播|点播|回放|录播|转播|重播|复播|首播|首映|首演|首秀|首发|首测|首试|首用|首购|首付|首贷|首保|首赔|首付|首期|首批|首次|第一|第二|第三|最后|最终|终极|结束|完成|成功|失败|错误|异常|故障|问题|缺陷|漏洞|补丁|更新|升级|版本|发布|上线|下线|停服|维护|修复|优化|改进|提升|增强|强化|新增|增加|添加|删除|移除|取消|关闭|暂停|停止|终止|结束|完成|成功|失败|错误|异常|故障|问题|缺陷|漏洞|补丁|更新|升级|版本|发布|上线|下线|停服|维护|修复|优化|改进|提升|增强|强化|新增|增加|添加|删除|移除|取消|关闭|暂停|停止|终止|结束|完成|成功|失败|错误|异常|故障|问题|缺陷|漏洞|补丁|更新|升级|版本|发布|上线|下线|停服|维护|修复|优化|改进|提升|增强|强化|限流|求助|联动|离线|误报|失控|云台|避障|跟随|追踪|手柄|配对|传感器|摄像头|无人机|抖动|悬停|图传|飞行|一键|多设备|执行|遥控器|空调|手表|震动|推送|续航|丢失|重新配对|失控|撞|坏了|失效|不执行|不工作|不运行|形同虚设|飘|偏|延迟|卡顿|卡死|闪退|崩溃|死机|白屏|黑屏|变砖|强制退出|ANR|扣款异常|重复扣款|不明扣款|打不开|一片空白|404|同步失败|数据异常|金额算错|乱码|订单消失|记录没了|聊天记录没了|验证码收不到|注册失败|被盗|被封|被限流|被禁言|被锁|封禁|风控|拦截|没到账|不到账|钱没到|扣了钱|订单没生成|多扣|金额不对|账单不对|没声音|播放不了|播放没声音|恢复不了|恢复失败|数据不同步|状态不同步|信息不同步|升级失败|识别不了|识别不通过|识别失败|定位飘|定位偏|定位不准|定位偏差|不见了|消失|丢失|被举报|限制转账|限制提现|账户限制|账户冻结|不工作|不运行|无法使用|不可用|扣了费|扣了钱|找不到了|显示空白|收藏夹空白|不执行|不生效|功能缺失|识别率低|成功率太低|误报|漏发|卡粮|上不了网|突然没了|离线频繁|频繁掉线|格式不对|出粮不均匀|不认了|不支持|做不到|不能自定义|识别不准|识别率太低|准确率太低|升级失败|变砖|关不掉|取消不了|停不了|无法撤回|紧急|求助|报警|SOS|求救|危险'
        if re.search(core_func_kw, text):
            priority = '高'
    if ptype == '体验' and priority == '低':
        exp_moderate_kw = r'涨了|翻倍|全是|根本|一直|太慢|太复杂|太繁琐|藏得|找不到|不解决|不处理|没人|不理|不管|骗|虚假|陷阱|套路|坑|差|烂|垃圾|恶心|气死|气炸|火大|无语|失望|寒心|过分|离谱|坑爹|坑人|霸王|欺负|歧视|区别对待|不公平|不一致|不一样|差太多|差远了|差很大|天差地别|趁火打劫|坐地起价|乱收费|多收费|重复收费|隐藏费用|强制消费|捆绑销售|诱导消费|虚假促销|虚假优惠|先涨后降|明降暗涨|货不对板|缺斤少两|以次充好|偷工减料|敷衍|推诿|踢皮球|不负责|不作为|不专业|不礼貌|态度恶劣|态度差|骂人|辱骂|威胁|恐吓|骚扰|疯狂|不停|一直打|轰炸|\d+天|一个月|开不了|看不懂|不灵活|不好用|不完整|不齐全|不全面|不详细|不准确|不靠谱|不放心|不踏实|不安心|不省心|担心|害怕|焦虑|着急|急死了|等不及|等不了|等不起|耗不起|耽误事|误事|坏事|出事|危险|风险|隐患|漏洞|缺陷|毛病|问题多|问题大|问题严重|频繁|经常|总是|老是|动不动|三天两头|隔三差五|没完没了|无休止|无止境|没个头|没完|不停|不断|连续|持续|反复|一再|多次|好几次|无数次|数不清|记不清|麻木|无奈|无力|无助|绝望|崩溃|疯了|受不了|忍不了|忍无可忍|不能再忍|忍到极限|极限|底线|红线|原则|尊严|人格|人权|权益|利益|损失|损害|伤害|受伤|受害|吃亏|上当|被骗|被坑|被宰|被割|被收割|被薅|被薅羊毛|被套路|被算计|被利用|被消费|被浪费|被耽误|被拖累|被连累|被牵连|被影响|被干扰|被打扰|被骚扰|被侵犯|被侵害|被损害|被破坏|被毁|被毁掉|被毁灭|被摧毁|被粉碎|被打破|被打乱|被搞乱|被弄乱|被搅乱|被扰乱|被干扰|被打断|被中断|被终止|被停止|被暂停|被取消|被关闭|被封锁|被屏蔽|被过滤|被审查|被监控|被跟踪|被监视|被监听|被偷窥|被偷看|被偷听|被偷拍|被偷录|被偷窃|被盗取|被盗用|被冒用|被冒充|被伪造|被篡改|被修改|被删除|被移除|被清空|被清零|被归零|被抹去|被抹掉|被擦除|被消除|被消灭|被抹杀|被扼杀|被扼制|被压制|被压抑|被抑制|被限制|被约束|被束缚|被捆绑|被绑架|被挟持|被威胁|被恐吓|被吓唬|被吓到|被吓坏|被吓傻|被吓呆|被吓懵|被吓晕|被吓死|被吓跑|被吓退|被吓走|被吓逃|被吓躲|被吓藏|被吓缩'
        if re.search(exp_moderate_kw, text):
            priority = '中'
    if ptype == '内容' and priority == '低':
        cnt_moderate_kw = r'完全|根本|太不|严重|错误|不对|过时|不一样|不一致|不公平|没法玩|没法用|全是|一直|骗|假|虚假|误导|不实|伪造|假冒|抄袭|剽窃|盗版|侵权|刷评|水军|假评'
        if re.search(cnt_moderate_kw, text):
            priority = '中'
    return priority


# === Test ===
total = len(feedbacks)
iron_caught = 0
iron_type_ok = 0
iron_sent_ok = 0
iron_prio_ok = 0
prio_dist = {'高': 0, '中': 0, '低': 0}

for fb in feedbacks:
    result = iron_classify_v6(fb['text'])
    if result is not None:
        iron_caught += 1
        ptype, sentiment, priority = result
        priority = apply_priority_rules(fb['text'], ptype, priority)
        if ptype == fb['gold_type']:
            iron_type_ok += 1
        if sentiment == fb['gold_sentiment']:
            iron_sent_ok += 1
        if priority == fb['gold_priority']:
            iron_prio_ok += 1
        prio_dist[priority] = prio_dist.get(priority, 0) + 1

iron_type_acc = round(iron_type_ok / iron_caught * 100, 1) if iron_caught else 0
iron_sent_acc = round(iron_sent_ok / iron_caught * 100, 1) if iron_caught else 0
iron_prio_acc = round(iron_prio_ok / iron_caught * 100, 1) if iron_caught else 0

print(f"Total: {total}")
print(f"Iron caught: {iron_caught}/{total} ({round(iron_caught/total*100,1)}%)")
print(f"Type accuracy: {iron_type_ok}/{iron_caught} ({iron_type_acc}%)")
print(f"Sentiment accuracy: {iron_sent_ok}/{iron_caught} ({iron_sent_acc}%)")
print(f"Priority accuracy: {iron_prio_ok}/{iron_caught} ({iron_prio_acc}%)")
print(f"\nPriority distribution: 高={prio_dist.get('高',0)}, 中={prio_dist.get('中',0)}, 低={prio_dist.get('低',0)}")

# Show some high/medium priority examples
print("\n=== High priority examples ===")
count = 0
for fb in feedbacks:
    result = iron_classify_v6(fb['text'])
    if result:
        ptype, sentiment, priority = result
        priority = apply_priority_rules(fb['text'], ptype, priority)
        if priority == '高' and count < 5:
            print(f"  [{ptype}/{sentiment}/{priority}] '{fb['text'][:60]}' (gold_prio={fb['gold_priority']})")
            count += 1

print("\n=== Medium priority examples ===")
count = 0
for fb in feedbacks:
    result = iron_classify_v6(fb['text'])
    if result:
        ptype, sentiment, priority = result
        priority = apply_priority_rules(fb['text'], ptype, priority)
        if priority == '中' and count < 5:
            print(f"  [{ptype}/{sentiment}/{priority}] '{fb['text'][:60]}' (gold_prio={fb['gold_priority']})")
            count += 1

# Priority misclassification detail
print("\n=== Priority misclassification ===")
prio_mis = {}
for fb in feedbacks:
    result = iron_classify_v6(fb['text'])
    if result:
        ptype, sentiment, priority = result
        priority = apply_priority_rules(fb['text'], ptype, priority)
        if priority != fb['gold_priority']:
            key = f"{fb['gold_priority']}→{priority}"
            prio_mis[key] = prio_mis.get(key, 0) + 1
for key, count in sorted(prio_mis.items(), key=lambda x: -x[1]):
    print(f"  {key}: {count}")
