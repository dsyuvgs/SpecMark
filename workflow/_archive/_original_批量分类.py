import json
import csv
import re

def main(file_content: list) -> dict:
    csv_headers = ['序号', '反馈内容', '问题类型', '情绪', '优先级', '隐含需求', '用户标签', '编号', '内容', '类型', '情感', '级别', '需求', '标签', 'id', 'content', 'type', 'sentiment', 'priority', 'need', 'tag', 'index', 'feedback', 'category', 'emotion', 'level', 'requirement', 'label', '品类', '场景', 'category', 'scene']
    feedback_col_names = {'内容', '文本', '反馈内容', 'content', 'description', '评论', '描述', 'feedback', 'text', '用户反馈', 'comment'}

    SCENE_CORE_MAP = {
        '电商': '搜索,购物车,下单,支付,退款,物流,评价,客服,商品,订单,优惠券,价格,会员,售后,发货,退货',
        '社交': '聊天,消息,好友,动态,评论,点赞,分享,群,朋友圈,私信,语音,视频,关注,粉丝,账号,登录',
        '金融': '转账,支付,余额,账单,还款,借款,理财,基金,股票,保险,信用,风控,银行卡,充值,提现',
        '教育': '课程,学习,作业,考试,成绩,老师,学生,班级,直播,录播,题库,练习,笔记,进度,证书',
        '外卖': '下单,配送,骑手,商家,餐品,订单,支付,退款,评价,客服,优惠券,红包,会员,地址',
        '出行': '打车,司机,路线,导航,地图,定位,行程,费用,支付,评价,客服,投诉,安全,紧急,拼车',
        '游戏': '登录,匹配,对战,充值,皮肤,英雄,角色,装备,技能,地图,服务器,延迟,卡顿,闪退,崩溃',
        '办公': '文档,表格,演示,协作,会议,日历,邮件,通讯录,审批,流程,项目,任务,日程,笔记,云盘',
        '医疗': '问诊,医生,处方,药品,挂号,预约,检查,报告,医保,支付,退款,评价,客服,投诉,推荐',
        '智能硬件': 'WiFi,蓝牙,配网,连接,固件,升级,地图,清扫,充电,回充,避障,吸力,噪音,续航,电池',
        '音乐': '播放,歌曲,歌单,搜索,推荐,下载,收藏,分享,歌词,音质,会员,付费,免费,广告,推送',
    }

    def detect_scene(text):
        best = ''
        best_score = 0
        for key, funcs in SCENE_CORE_MAP.items():
            kws = funcs.split(',')
            score = sum(1 for k in kws if k in text)
            if score > best_score:
                best_score = score
                best = key
        return best if best_score >= 1 else ''

    def extract_tags(text):
        tags = []
        if re.search(r'(会员|VIP|充值|付费|订阅|充了|花钱)', text):
            tags.append('付费用户')
        if re.search(r'(刚买|刚注册|第一次用|新手)', text):
            tags.append('新用户')
        if re.search(r'(用了.*月|用了.*年|老用户|用了很久)', text):
            tags.append('老用户')
        return tags

    def extract_need(text):
        mappings = [
            (r'每次都要(.{2,6})', '自动化'),
            (r'找不到(.{2,6})', '入口优化'),
            (r'太麻烦了|太复杂', '流程简化'),
            (r'能不能(加个|增加|支持)(.{2,8})', None),
            (r'希望(增加|支持|有)(.{2,8})', None),
            (r'噪音太大|太吵', '静音模式'),
            (r'充电太慢|充电.*慢', '快充'),
            (r'总是断连|断连', '连接稳定性'),
            (r'没有(.{2,6})模式', None),
        ]
        for pattern, need in mappings:
            m = re.search(pattern, text)
            if m:
                if need:
                    return need
                groups = m.groups()
                if len(groups) >= 2 and groups[-1]:
                    return groups[-1][:12]
                elif len(groups) >= 1 and groups[0]:
                    return groups[0][:12]
        return '无'

    def iron_classify(text):
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
            r'对不上|多扣|金额不对|账单不对|'
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
            r'数据不同步|状态不同步|信息不同步',
            text
        ))
        has_content_issue = bool(re.search(
            r'图文不符|描述不符|实物不符|货不对板|缺斤少两|'
            r'虚假宣传|夸大宣传|误导|标称|标示|'
            r'推荐不准|推荐不好|搜索不对|搜不到|搜出来不对|'
            r'匹配不公|匹配机制|算法有问题|'
            r'翻译错|字幕不同步|歌词延迟|歌词翻译不对|'
            r'内容过时|信息旧|攻略过时|信息过时|'
            r'数据有延迟|数据延迟|不准确|不准|算错|'
            r'答案有错|题库.*错|不完整',
            text
        ))
        exp_surface_keywords = ['退款', '售后', '客服', '骑手', '司机', '商家', '配送',
                                '退货', '换货', '拒赔', '投诉', '举报']
        has_exp_surface = any(k in text for k in exp_surface_keywords)
        if has_func_failure and has_exp_surface:
            func_high_kw = ['支付', '扣款', '订单', '账号', '登录', '数据', '账单',
                            '同步失败', '丢失', '消失', '被盗', '被封', '封禁', '锁了',
                            '风控', '转账', '到账', '隐私', '泄露', '报错', '失败',
                            '闪退', '崩溃', '死机', '白屏', '黑屏', '打不开', '用不了',
                            '不能用', '没法用', '连不上', '掉线', '断连', '没反应',
                            '被锁', '拦截', '限制', '冻结', '多扣', '对不上', '没到账',
                            '关不掉', '取消不了', '扣了']
            if any(k in text for k in func_high_kw):
                return ('功能', '负向', '高')
            return ('功能', '负向', '中')
        if has_content_issue and has_exp_surface:
            content_high_kw = ['不符', '虚假', '夸大', '误导', '缺斤少两', '货不对板']
            if any(k in text for k in content_high_kw):
                return ('内容', '负向', '中')
            return ('内容', '负向', '低')
        func_rules = [
            (['闪退', '崩溃', '死机', '白屏', '黑屏', '变砖', '强制退出', 'ANR'], '功能', '负向', '高'),
            (['支付失败', '扣款异常', '重复扣款', '数据丢失', '登录不上', '账号被盗',
              '隐私泄露', '隐私暴露', '不明扣款'], '功能', '负向', '高'),
            (['打不开', '一片空白', '404', '功能失效', '没反应', '报错',
              '上传失败', '下载失败', '保存失败', '同步失败',
              '不能用', '没法用', '用不了', '无响应', '失效', '失灵',
              '保存不了', '传不了', '下不了', '载不出'], '功能', '负向', '高'),
            (['掉线', '断连', '无法连接', '连不上', '连接失败', '断开'], '功能', '负向', '高'),
            (['验证码收不到', '注册失败'], '功能', '负向', '高'),
            (['被盗', '被封', '被限流', '被禁言'], '功能', '负向', '高'),
            (['数据异常', '金额算错', '乱码', '订单消失', '记录没了', '聊天记录没了'], '功能', '负向', '高'),
            (['卡死无法', '卡死不能', '无法跳转'], '功能', '负向', '高'),
            (['形同虚设', '绕过', '绕开'], '功能', '负向', '高'),
            (['识别不准', '识别率太低', '准确率太低'], '功能', '负向', '中'),
            (['被锁', '封禁', '风控', '拦截'], '功能', '负向', '高'),
            (['没到账', '不到账', '对不上', '多扣'], '功能', '负向', '高'),
            (['没声音', '播放不了', '播放没声音'], '功能', '负向', '高'),
            (['恢复不了', '恢复失败'], '功能', '负向', '高'),
            (['账户限制', '账户冻结', '限制转账', '限制提现'], '功能', '负向', '高'),
            (['审核不通过', '审核拒绝'], '功能', '负向', '高'),
        ]
        svc_rules = [
            (['配送超时', '配送慢', '餐品凉', '洒了', '扔门口', '送餐慢',
              '骑手态度', '司机态度', '骑手恶劣', '司机绕路', '提前确认送达'], '体验', '负向', '高'),
            (['吃出异物', '食物变质', '食品安全', '餐品变质', '寄生虫'], '体验', '负向', '高'),
            (['商家取消', '商家不承认', '商家不管', '拒赔', '拒不赔偿',
              '拒绝退款', '拒绝理赔'], '体验', '负向', '高'),
            (['自动续费', '大数据杀熟', '杀熟'], '体验', '负向', '高'),
            (['客服不管', '客服不解决', '客服推诿', '客服机器人', '客服打不通',
              '客服态度', '模板话术', '没人处理', '推诿责任', '不作为'], '体验', '负向', '中'),
            (['退款慢', '售后慢', '审核太慢', '退款等了', '售后审核'], '体验', '负向', '中'),
            (['臭车', '卫生环境', '异味', '车内异味'], '体验', '负向', '中'),
            (['不安全驾驶', '安全隐患'], '体验', '负向', '高'),
        ]
        perf_rules = [
            (['卡顿', '太卡了', '很卡', '变卡', '不流畅',
              '卡得', '卡的要死', '卡死了', '卡的要命'], '性能', '负向', '中'),
            (['加载慢', '启动慢', '打开慢', '响应慢', '运行慢',
              '限速', '上传限速'], '性能', '负向', '中'),
            (['延迟高', '网络延迟', '高延迟', '延迟太大', '延迟严重'], '性能', '负向', '中'),
            (['耗电', '费电', '掉电快', '发烫', '过热',
              '续航虚标', '续航差', '电池掉电'], '性能', '负向', '中'),
            (['掉帧', '帧率低', '不跟手', '画面不流畅'], '性能', '负向', '中'),
            (['缓冲', '转圈圈', '一直转圈', 'loading', '缓冲中', '转半天'], '性能', '负向', '中'),
            (['占用高', '内存高', '资源占用', '假死', 'CPU高',
              '占用太大', '占用太多', '包太大', '安装包大', '更新包大'], '性能', '负向', '中'),
            (['画面延迟', '声音延迟', '画面不同步', '声音不同步'], '性能', '负向', '中'),
        ]
        content_rules = [
            (['推荐不准', '推荐不好', '推荐单一', '推荐重复', '推荐过时',
              '推荐越来越', '同质化'], '内容', '负向', '中'),
            (['搜索不对', '搜不到', '搜出来不对', '搜索结果不相关',
              '版权覆盖太少'], '内容', '负向', '中'),
            (['匹配不公', '匹配机制', '算法有问题', '算法推荐'], '内容', '负向', '中'),
            (['翻译错', '字幕不同步', '歌词延迟', '歌词翻译不对'], '内容', '负向', '中'),
            (['图文不符', '描述不符', '实物不符', '刷评', '水军',
              '内容过时', '信息旧', '攻略过时', '信息过时'], '内容', '负向', '中'),
            (['黄色', '暧昧信息', '低俗', '戾气'], '内容', '负向', '中'),
            (['数据有延迟', '数据延迟'], '内容', '负向', '低'),
            (['虚假宣传', '夸大宣传', '缺斤少两', '货不对板'], '内容', '负向', '中'),
        ]
        suggest_rules = [
            (['能不能', '希望', '建议', '想要', '加个', '能不能加'], '体验', '中性', '低'),
        ]
        other_exp_rules = [
            (['广告', '推送太多', '操作复杂', '找不到入口', '太贵', '涨价',
              '诱导', '套路', '权益缩水', 'VIP专属', '免费用户', '吃相'], '体验', '负向', '低'),
            (['太麻烦', '繁琐', '找不到', '难找', '不方便', '不好用',
              '难用', '步骤太多', '设置太深', '隐藏得太深', '太复杂'], '体验', '负向', '低'),
            (['预售', '发货时间', '没发货', '物流', '发货'], '体验', '负向', '中'),
            (['配送费'], '体验', '负向', '低'),
        ]
        all_rules = func_rules + svc_rules + perf_rules + content_rules + suggest_rules + other_exp_rules
        for keywords, ptype, sentiment, priority in all_rules:
            if any(k in text for k in keywords):
                return (ptype, sentiment, priority)
        if re.search(r'(?:太|很|特别|变|更|越|也|都|还是|就是).*卡|卡(?:顿|住|得|的|了)', text):
            if not re.search(r'银行卡|打卡|会员卡|卡通|卡片|卡包', text):
                return ('性能', '负向', '中')
        if re.search(r'(?:太|很|特别|更|越).*慢|慢(?:了|得|的)', text):
            if not re.search(r'回复.*慢|问诊|医生|客服.*慢|退款|售后|审核|物流|发货|配送', text):
                return ('性能', '负向', '中')
        if re.search(r'启动.{0,3}\d+秒|启动要|打开要', text):
            return ('性能', '负向', '中')
        if '续航' in text:
            return ('性能', '负向', '中')
        if '假死' in text:
            return ('性能', '负向', '中')
        if '限速' in text:
            return ('性能', '负向', '中')
        if re.search(r'(?:资源|内存|CPU).*(?:占用|高|大|太多)', text):
            return ('性能', '负向', '中')
        if re.search(r'转.{0,3}圈', text):
            if not re.search(r'朋友圈|社交圈', text):
                return ('性能', '负向', '中')
        if re.search(r'手机.{0,3}烫|烫.{0,3}手', text):
            return ('性能', '负向', '中')
        if re.search(r'延迟.{0,4}(?:大|严重|高|太多)', text):
            if not re.search(r'数据.*延迟|汇率.*延迟|牌价.*延迟', text):
                return ('性能', '负向', '中')
        if re.search(r'不同步', text):
            if re.search(r'数据|状态|信息|订单|库存|记录', text):
                return ('功能', '负向', '中')
            if not re.search(r'字幕|歌词|翻译', text):
                return ('性能', '负向', '中')
        if re.search(r'数据.{0,2}延迟|汇率.*延迟|牌价.*延迟', text):
            return ('内容', '负向', '低')
        if '描述不符' in text or '实物不符' in text or '缺斤少两' in text:
            return ('内容', '负向', '中')
        if re.search(r'刷.{0,1}评|假评|水军|五星好评', text):
            return ('内容', '负向', '中')
        if '杀熟' in text:
            return ('体验', '负向', '高')
        if re.search(r'关不掉|取消不了|停不了', text):
            return ('功能', '负向', '中')
        if re.search(r'退款|售后|退货|换货|拒赔', text):
            if has_func_failure:
                return ('功能', '负向', '高')
            return ('体验', '负向', '低')
        if re.search(r'配送|骑手|司机|打车|叫车|网约车|顺风车|拼车|接单|接机', text):
            if has_func_failure:
                return ('功能', '负向', '中')
            return ('体验', '负向', '低')
        if '客服' in text:
            if has_func_failure:
                return ('功能', '负向', '高')
            return ('体验', '负向', '中')
        if re.search(r'广告|推送|弹窗|开屏', text):
            return ('体验', '负向', '低')
        if re.search(r'太贵|涨价|价格|不值|性价比|抽奖|充更多', text):
            return ('体验', '负向', '低')
        if re.search(r'会员|VIP|付费|充值|续费|红包|权益', text):
            return ('体验', '负向', '低')
        if re.search(r'能不能|希望|建议|想要|加个', text):
            return ('体验', '中性', '低')
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
        if re.search(r'审核不通过|审核.*拒绝', text):
            return ('功能', '负向', '高')
        if re.search(r'额度太低|额度不够', text):
            return ('体验', '负向', '低')
        if re.search(r'到店.*没房|预订.*没房|没房了', text):
            return ('体验', '负向', '高')
        if re.search(r'没人接单|没接单', text):
            return ('体验', '负向', '中')
        if re.search(r'次日达|等了\d+天|等了\d+分钟', text):
            return ('体验', '负向', '中')
        if re.search(r'信息过时|早就关门|攻略.*过时', text):
            return ('内容', '负向', '中')
        if re.search(r'规则不透明|不透明', text):
            return ('体验', '负向', '低')
        if re.search(r'威胁|骚扰|疯狂打电话', text):
            return ('体验', '负向', '高')
        if re.search(r'重影|竖条|刮痕|显示屏', text):
            return ('体验', '负向', '高')
        if re.search(r'运费|退货.*运费', text):
            return ('体验', '负向', '低')
        if re.search(r'材质.*不符|手感.*不一样', text):
            return ('内容', '负向', '中')
        if re.search(r'功能臃肿|臃肿|花里胡哨', text):
            return ('体验', '负向', '低')
        if re.search(r'bug|Bug|BUG', text):
            return ('功能', '负向', '中')
        if re.search(r'崩了|大面积故障|服务异常', text):
            return ('功能', '负向', '高')
        if re.search(r'识别为外出|打卡.*迟到|打卡.*外勤', text):
            return ('功能', '负向', '高')
        if re.search(r'付费推广|前五页', text):
            return ('体验', '负向', '中')
        if re.search(r'已读回执|已读', text):
            return ('体验', '中性', '低')
        return None
        func_rules = [
            (['闪退', '崩溃', '死机', '白屏', '黑屏', '变砖', '强制退出', 'ANR'], '功能', '负向', '高'),
            (['支付失败', '扣款异常', '重复扣款', '数据丢失', '登录不上', '账号被盗',
              '隐私泄露', '隐私暴露', '不明扣款'], '功能', '负向', '高'),
            (['打不开', '一片空白', '404', '功能失效', '没反应', '报错',
              '上传失败', '下载失败', '保存失败', '同步失败',
              '不能用', '没法用', '用不了', '无响应', '失效', '失灵',
              '保存不了', '传不了', '下不了', '载不出'], '功能', '负向', '高'),
            (['掉线', '断连', '无法连接', '连不上', '连接失败', '断开'], '功能', '负向', '高'),
            (['验证码收不到', '注册失败'], '功能', '负向', '高'),
            (['被盗', '被封', '被限流', '被禁言'], '功能', '负向', '高'),
            (['数据异常', '金额算错', '乱码', '订单消失', '记录没了', '聊天记录没了'], '功能', '负向', '高'),
            (['卡死无法', '卡死不能', '无法跳转'], '功能', '负向', '高'),
            (['形同虚设', '绕过', '绕开'], '功能', '负向', '高'),
            (['识别不准', '识别率太低', '准确率太低'], '功能', '负向', '中'),
        ]
        svc_rules = [
            (['配送超时', '配送慢', '餐品凉', '洒了', '扔门口', '送餐慢',
              '骑手态度', '司机态度', '骑手恶劣', '司机绕路', '提前确认送达'], '体验', '负向', '高'),
            (['吃出异物', '食物变质', '食品安全', '餐品变质', '寄生虫'], '体验', '负向', '高'),
            (['商家取消', '商家不承认', '商家不管', '拒赔', '拒不赔偿',
              '拒绝退款', '拒绝理赔'], '体验', '负向', '高'),
            (['自动续费', '虚假宣传', '大数据杀熟', '杀熟'], '体验', '负向', '高'),
            (['客服不管', '客服不解决', '客服推诿', '客服机器人', '客服打不通',
              '客服态度', '模板话术', '没人处理', '推诿责任', '不作为'], '体验', '负向', '中'),
            (['退款慢', '售后慢', '审核太慢', '退款等了', '售后审核'], '体验', '负向', '中'),
            (['臭车', '卫生环境', '异味', '车内异味'], '体验', '负向', '中'),
            (['不安全驾驶', '安全隐患'], '体验', '负向', '高'),
        ]
        perf_rules = [
            (['卡顿', '太卡了', '很卡', '变卡', '不流畅',
              '卡得', '卡的要死', '卡死了', '卡的要命'], '性能', '负向', '中'),
            (['加载慢', '启动慢', '打开慢', '响应慢', '运行慢',
              '限速', '上传限速'], '性能', '负向', '中'),
            (['延迟高', '网络延迟', '高延迟'], '性能', '负向', '中'),
            (['耗电', '费电', '掉电快', '发烫', '过热',
              '续航虚标', '续航差', '电池掉电'], '性能', '负向', '中'),
            (['掉帧', '帧率低', '不跟手', '画面不流畅'], '性能', '负向', '中'),
            (['缓冲', '转圈圈', '一直转圈', 'loading', '缓冲中', '转半天'], '性能', '负向', '中'),
            (['占用高', '内存高', '资源占用', '假死', 'CPU高',
              '占用太大', '占用太多', '包太大', '安装包大', '更新包大'], '性能', '负向', '中'),
        ]
        content_rules = [
            (['推荐不准', '推荐不好', '推荐单一', '推荐重复', '推荐过时',
              '推荐越来越', '同质化'], '内容', '负向', '中'),
            (['搜索不对', '搜不到', '搜出来不对', '搜索结果不相关',
              '版权覆盖太少'], '内容', '负向', '中'),
            (['匹配不公', '匹配机制', '算法有问题', '算法推荐'], '内容', '负向', '中'),
            (['翻译错', '字幕不同步', '歌词延迟', '歌词翻译不对'], '内容', '负向', '中'),
            (['图文不符', '描述不符', '实物不符', '刷评', '水军',
              '内容过时', '信息旧', '攻略过时', '信息过时'], '内容', '负向', '中'),
            (['黄色', '暧昧信息', '低俗', '戾气'], '内容', '负向', '中'),
            (['数据有延迟', '数据延迟'], '内容', '负向', '低'),
        ]
        suggest_rules = [
            (['能不能', '希望', '建议', '想要', '加个', '能不能加'], '体验', '中性', '低'),
        ]
        other_exp_rules = [
            (['广告', '推送太多', '操作复杂', '找不到入口', '太贵', '涨价',
              '会员', '退款', '售后', '诱导', '套路', '权益缩水',
              'VIP专属', '免费用户', '吃相'], '体验', '负向', '低'),
            (['太麻烦', '繁琐', '找不到', '难找', '不方便', '不好用',
              '难用', '步骤太多', '设置太深', '隐藏得太深', '太复杂'], '体验', '负向', '低'),
            (['预售', '发货时间', '没发货', '物流', '发货'], '体验', '负向', '中'),
            (['配送费'], '体验', '负向', '低'),
        ]
        all_rules = func_rules + svc_rules + perf_rules + content_rules + suggest_rules + other_exp_rules
        for keywords, ptype, sentiment, priority in all_rules:
            if any(k in text for k in keywords):
                return (ptype, sentiment, priority)
        if re.search(r'(?:太|很|特别|变|更|越|也|都|还是|就是).*卡|卡(?:顿|住|得|的|了)', text):
            if not re.search(r'银行卡|打卡|会员卡|卡通|卡片|卡包', text):
                return ('性能', '负向', '中')
        if re.search(r'(?:太|很|特别|更|越).*慢|慢(?:了|得|的)', text):
            if not re.search(r'回复.*慢|问诊|医生|客服.*慢|退款|售后|审核|物流|发货|配送', text):
                return ('性能', '负向', '中')
        if re.search(r'启动.{0,3}\d+秒|启动要|打开要', text):
            return ('性能', '负向', '中')
        if '续航' in text:
            return ('性能', '负向', '中')
        if '假死' in text:
            return ('性能', '负向', '中')
        if '限速' in text:
            return ('性能', '负向', '中')
        if re.search(r'(?:资源|内存|CPU).*(?:占用|高|大|太多)', text):
            return ('性能', '负向', '中')
        if re.search(r'转.{0,3}圈', text):
            if not re.search(r'朋友圈|社交圈', text):
                return ('性能', '负向', '中')
        if re.search(r'手机.{0,3}烫|烫.{0,3}手', text):
            return ('性能', '负向', '中')
        if re.search(r'数据.{0,2}延迟|汇率.*延迟|牌价.*延迟', text):
            return ('内容', '负向', '低')
        if '描述不符' in text or '实物不符' in text or '缺斤少两' in text:
            return ('内容', '负向', '中')
        if re.search(r'刷.{0,1}评|假评|水军|五星好评', text):
            return ('内容', '负向', '中')
        if '杀熟' in text:
            return ('体验', '负向', '高')
        if re.search(r'退款|售后|退货|换货|拒赔', text):
            return ('体验', '负向', '低')
        if re.search(r'配送|骑手|司机|打车|叫车|网约车|顺风车|拼车|接单|接机', text):
            return ('体验', '负向', '低')
        if '客服' in text:
            return ('体验', '负向', '中')
        if re.search(r'广告|推送|弹窗|开屏', text):
            return ('体验', '负向', '低')
        if re.search(r'太贵|涨价|价格|不值|性价比|抽奖|充更多', text):
            return ('体验', '负向', '低')
        if re.search(r'会员|VIP|付费|充值|续费|红包|权益', text):
            return ('体验', '负向', '低')
        if re.search(r'能不能|希望|建议|想要|加个', text):
            return ('体验', '中性', '低')
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
        if re.search(r'审核不通过|审核.*拒绝', text):
            return ('功能', '负向', '高')
        if re.search(r'额度太低|额度不够', text):
            return ('体验', '负向', '低')
        if re.search(r'到店.*没房|预订.*没房|没房了', text):
            return ('体验', '负向', '高')
        if re.search(r'没人接单|没接单', text):
            return ('体验', '负向', '中')
        if re.search(r'次日达|等了\d+天|等了\d+分钟', text):
            return ('体验', '负向', '中')
        if re.search(r'信息过时|早就关门|攻略.*过时', text):
            return ('内容', '负向', '中')
        if re.search(r'规则不透明|不透明', text):
            return ('体验', '负向', '低')
        if re.search(r'威胁|骚扰|疯狂打电话', text):
            return ('体验', '负向', '高')
        if re.search(r'重影|竖条|刮痕|显示屏', text):
            return ('体验', '负向', '高')
        if re.search(r'运费|退货.*运费', text):
            return ('体验', '负向', '低')
        if re.search(r'材质.*不符|手感.*不一样', text):
            return ('内容', '负向', '中')
        if re.search(r'功能臃肿|臃肿|花里胡哨', text):
            return ('体验', '负向', '低')
        if re.search(r'bug|Bug|BUG', text):
            return ('功能', '负向', '中')
        if re.search(r'崩了|大面积故障|服务异常', text):
            return ('功能', '负向', '高')
        if re.search(r'不实时同步|不.*同步|要刷新', text):
            return ('功能', '负向', '中')
        if re.search(r'识别为外出|打卡.*迟到|打卡.*外勤', text):
            return ('功能', '负向', '高')
        if re.search(r'付费推广|前五页', text):
            return ('体验', '负向', '中')
        if re.search(r'已读回执|已读', text):
            return ('体验', '中性', '低')
        return None

    def is_header_row(text):
        t = text.strip().strip(',').strip('|').strip()
        t = t.lstrip('\ufeff')
        if not t:
            return True
        clean = t.replace(' ', '').replace('|', '')
        if clean.startswith('---') or clean.startswith('===') or clean.startswith('+++'):
            return True
        if re.match(r'^[-=+]{3,}$', clean):
            return True
        parts = [p.strip().lstrip('\ufeff') for p in t.replace('|', ',').split(',') if p.strip()]
        if len(parts) >= 2:
            header_count = sum(1 for p in parts if p in csv_headers)
            if header_count >= 2:
                return True
        return False

    def flatten_to_lines(file_content):
        lines = []
        for item in file_content:
            text = str(item).strip().lstrip('\ufeff')
            if not text:
                continue
            if '\n' in text:
                for line in text.split('\n'):
                    line = line.strip().lstrip('\ufeff')
                    if line:
                        lines.append(line)
            else:
                lines.append(text)
        return lines

    def extract_feedback_text(line, header_fields, feedback_col_idx):
        sep = ','
        if '|' in line and line.strip().count('|') >= 2:
            sep = '|'
        if sep == '|':
            parts = [p.strip() for p in line.strip('|').split('|') if p.strip()]
        else:
            try:
                parsed = list(csv.reader([line]))
                parts = parsed[0] if parsed else [line]
            except Exception:
                parts = [p.strip() for p in line.split(',') if p.strip()]
        if feedback_col_idx is not None and feedback_col_idx < len(parts):
            val = parts[feedback_col_idx].strip()
            if val:
                return val
        if len(parts) >= 2:
            for i, val in enumerate(parts):
                val = val.strip()
                if val and not val.isdigit():
                    return val
            return parts[1].strip()
        return line.strip()

    all_lines = flatten_to_lines(file_content)

    header_line = None
    header_fields = []
    feedback_col_idx = None
    data_lines = []

    for line in all_lines:
        if is_header_row(line) and header_line is None:
            header_line = line
            line_clean = line.strip('|').strip().lstrip('\ufeff')
            sep = ','
            if '|' in line_clean and line_clean.count('|') >= 2:
                sep = '|'
            if sep == '|':
                header_fields = [f.strip() for f in line_clean.strip('|').split('|') if f.strip()]
            else:
                try:
                    parsed = list(csv.reader([line_clean]))
                    if parsed:
                        header_fields = [f.strip() for f in parsed[0]]
                except Exception:
                    header_fields = [f.strip() for f in line_clean.replace('|', ',').split(',') if f.strip()]
            for i, h in enumerate(header_fields):
                if h in feedback_col_names:
                    feedback_col_idx = i
                    break
        elif not is_header_row(line):
            data_lines.append(line)

    results = []
    for idx, line in enumerate(data_lines, 1):
        if header_fields:
            feedback_text = extract_feedback_text(line, header_fields, feedback_col_idx)
        else:
            parts = list(csv.reader([line]))
            if parts and len(parts[0]) >= 2:
                candidates = [p.strip() for p in parts[0] if p.strip() and not p.strip().isdigit()]
                feedback_text = candidates[0] if candidates else line
            else:
                feedback_text = line

        if not feedback_text:
            continue

        result = iron_classify(feedback_text)
        if result:
            ptype, sentiment, priority = result
        else:
            ptype = '体验'
            sentiment = '中性'
            priority = '低'

        scene = detect_scene(feedback_text)
        tags = extract_tags(feedback_text)
        need = extract_need(feedback_text)

        results.append({
            "index": idx,
            "text": feedback_text[:100],
            "problem_type": ptype,
            "sentiment": sentiment,
            "priority": priority,
            "scene": scene,
            "user_tags": ', '.join(tags) if tags else '无',
            "implicit_need": need
        })

    return {
        "output": json.dumps(results, ensure_ascii=False),
        "total": len(results)
    }
