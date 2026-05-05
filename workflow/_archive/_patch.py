# _patch.py — 给三个代码节点补全 KB v6.0 优先级后处理规则
# 2026-05-05: 缓解词降级 + 核心功能提升

import re

with open('SpecMark最新.yml', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 新增函数：apply_priority_rules
# ============================================================
HELPER_FUNC = '''              def apply_priority_rules(text, ptype, priority):
                  # apply_priority_rules v6.2 2026-05-05
                  # KB v6.0 Section 四: mitigation downgrade + core function boost
                  mitigation_kw = r'偶尔|有时|不影响使用|但整体|但基本|还行|勉强|凑合|一般般|还能用|将就|忍了|可以接受'
                  no_downgrade_kw = r'闪退|崩溃|死机|数据丢失|支付失败|安全漏洞|食品安全|异物|变质|被欺骗|自动续费|虚假宣传'
                  if re.search(mitigation_kw, text) and not re.search(no_downgrade_kw, text):
                      if priority == '高':
                          priority = '中'
                      elif priority == '中':
                          priority = '低'
                  if ptype == '功能' and priority == '中':
                      core_func_kw = r'支付|登录|下单|订单|转账|账户|交易|充值|提现|扣款|付款|退款|到账|余额|账单|注册|认证|安全|隐私|数据|同步|备份|导出|播放|上传|下载|发送|接收|消息|通知|会员|订阅|续费|匹配|导航|定位|预订|叫车|打车|挂号|问诊|处方|搜索|收藏|评论|分享|点赞|关注|直播|视频|语音|通话|打卡|签到|积分|优惠券|红包|取消|路线|行程|配送|物流|发货|收货|库存|售后|客服|菜单|购物车|商品|秒杀|抽卡|存档|联机|组队|更新|升级|安装|卸载|绑定|解绑|实名|验证|密码|短信|邮箱|手机|人脸|指纹|识别|验证码|注册|注销|激活|开通|关闭|暂停|恢复|重置|修改|变更|迁移|导入|导出|备份|还原|同步|合并|拆分|排序|筛选|过滤|分类|标签|标记|收藏|点赞|评论|回复|转发|分享|举报|投诉|反馈|建议|意见|评价|评分|打分|投票|问卷|调查|调研|测试|试用|体验|预览|演示|展示|推荐|推送|通知|提醒|消息|私信|聊天|对话|会话|通话|视频|语音|直播|播放|暂停|停止|快进|快退|跳过|循环|随机|顺序|列表|歌单|专辑|歌手|歌曲|音乐|音频|声音|音量|音质|音效|均衡|歌词|字幕|翻译|配音|解说|讲解|教程|课程|学习|培训|教育|考试|测验|作业|任务|项目|计划|日程|日历|时间|日期|提醒|闹钟|计时|倒计|秒表|计算|换算|汇率|单位|长度|重量|温度|天气|地图|导航|路线|交通|公交|地铁|火车|飞机|酒店|民宿|景点|门票|攻略|游记|签证|护照|保险|医疗|健康|运动|健身|跑步|骑行|游泳|瑜伽|冥想|睡眠|饮食|营养|食谱|菜谱|烹饪|烘焙|甜点|饮品|咖啡|茶|酒|饮料|水果|蔬菜|肉类|海鲜|零食|小吃|外卖|配送|快递|物流|包裹|邮件|短信|电话|通讯|联系|地址|位置|坐标|经纬|海拔|高度|深度|距离|面积|体积|重量|温度|湿度|气压|风速|风向|降水|天气|气候|环境|生态|自然|动物|植物|生物|化学|物理|数学|统计|概率|逻辑|推理|判断|决策|选择|优化|改进|提升|增强|强化|学习|训练|练习|复习|预习|准备|计划|安排|组织|管理|领导|指挥|协调|沟通|交流|合作|协作|团队|小组|部门|公司|企业|组织|机构|单位|学校|医院|银行|政府|军队|警察|消防|急救|救援|应急|危机|风险|安全|保护|防护|防御|攻击|入侵|病毒|木马|蠕虫|间谍|黑客|破解|盗版|侵权|抄袭|剽窃|伪造|假冒|欺诈|诈骗|欺骗|误导|虚假|不实|谣言|传言|传闻|消息|新闻|资讯|信息|数据|资料|文件|文档|报告|报表|图表|图形|图像|图片|照片|视频|音频|音乐|歌曲|电影|电视|节目|频道|电台|广播|直播|点播|回放|录播|转播|重播|复播|首播|首映|首演|首秀|首发|首测|首试|首用|首购|首付|首贷|首保|首赔|首付|首期|首批|首次|第一|第二|第三|最后|最终|终极|结束|完成|成功|失败|错误|异常|故障|问题|缺陷|漏洞|补丁|更新|升级|版本|发布|上线|下线|停服|维护|修复|优化|改进|提升|增强|强化|新增|增加|添加|删除|移除|取消|关闭|暂停|停止|终止|结束|完成|成功|失败|错误|异常|故障|问题|缺陷|漏洞|补丁|更新|升级|版本|发布|上线|下线|停服|维护|修复|优化|改进|提升|增强|强化|新增|增加|添加|删除|移除|取消|关闭|暂停|停止|终止|结束|完成|成功|失败|错误|异常|故障|问题|缺陷|漏洞|补丁|更新|升级|版本|发布|上线|下线|停服|维护|修复|优化|改进|提升|增强|强化'
                      if re.search(core_func_kw, text):
                          priority = '高'
                  return priority
'''

# ============================================================
# 找到三个 iron_classify 的 return None 位置并插入 HELPER_FUNC
# ============================================================

iron_starts = list(re.finditer(r'def iron_classify\(text\):', content))
print(f'找到 iron_classify 定义: {len(iron_starts)} 处')

pat_end = r'              return None\n\n              result = iron_classify'
matches = list(re.finditer(pat_end, content))
print(f'找到 iron_classify 末尾 (节点1/2): {len(matches)} 处')

pat_end3 = r'              return None\n\n          for idx, line in enumerate'
matches3 = list(re.finditer(pat_end3, content))
print(f'找到 iron_classify 末尾 (节点3): {len(matches3)} 处')

all_matches = []
for m in matches:
    all_matches.append((m.start(), 'node12'))
for m in matches3:
    all_matches.append((m.start(), 'node3'))
all_matches.sort(reverse=True)

for pos, ntype in all_matches:
    insert_pos = pos + len('              return None\n')
    content = content[:insert_pos] + HELPER_FUNC + '\n' + content[insert_pos:]

print('已插入 apply_priority_rules 函数')

# ============================================================
# 修改调用逻辑
# ============================================================

old_call_12 = '''              result = iron_classify(text)
              if result:
                  ptype, sentiment, priority = result
                  source = '铁律拦截\''''
new_call_12 = '''              result = iron_classify(text)
              if result:
                  ptype, sentiment, priority = result
                  priority = apply_priority_rules(text, ptype, priority)
                  source = '铁律拦截\''''

count12 = content.count(old_call_12)
content = content.replace(old_call_12, new_call_12)
print(f'节点1/2 调用逻辑修改: {count12} -> {content.count(new_call_12)}')

old_call_3 = '''                  result = iron_classify(feedback_text)
                  if result:
                      ptype, sentiment, iron_priority = result
                      priority = iron_priority if iron_priority is not None else '低'
                  else:
                      ptype = '体验'
                      sentiment = '中性'
                      priority = '低\''''
new_call_3 = '''                  result = iron_classify(feedback_text)
                  if result:
                      ptype, sentiment, iron_priority = result
                      priority = iron_priority if iron_priority is not None else '低'
                      priority = apply_priority_rules(feedback_text, ptype, priority)
                  else:
                      ptype = '体验'
                      sentiment = '中性'
                      priority = '低\''''

count3 = content.count(old_call_3)
content = content.replace(old_call_3, new_call_3)
print(f'节点3 调用逻辑修改: {count3} -> {content.count(new_call_3)}')

# ============================================================
# 写入
# ============================================================
with open('SpecMark最新.yml', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n✅ 补丁完成')
print(f'文件大小: {len(content)} 字符')
print(f'iron_classify 定义: {len(re.findall(r"def iron_classify\(text\):", content))} 处')
print(f'apply_priority_rules 定义: {len(re.findall(r"def apply_priority_rules", content))} 处')
print(f'调用 apply_priority_rules(text: {len(re.findall(r"apply_priority_rules\(text", content))} 处')
print(f'调用 apply_priority_rules(feedback: {len(re.findall(r"apply_priority_rules\(feedback", content))} 处')
