import json
import random
import os

random.seed(42)

reviews = []

navigation = [
    "机器人总是迷路，找不到充电座，每次都要我手动搬回去",
    "导航太差了，同一个房间扫了三遍，另一个房间完全没进去",
    "建图功能就是个笑话，每次开机地图都不一样",
    "总是卡在沙发底下出不来，一天要救它好几次",
    "避障功能形同虚设，每次都撞桌腿，撞得砰砰响",
    "说好的智能路径规划，实际就是随机乱转，跟几百块的没区别",
    "地图总是丢失，每周都要重新建图，烦死了",
    "充电座就在旁边，它转了半小时都找不到，最后没电停在地中间",
    "每次扫到一半就迷路了，开始原地打转，浪费电",
    "避障传感器明显有问题，我家的椅子腿都被撞出划痕了",
    "它看到障碍物不是绕过去，而是直接放弃那片区域，覆盖率只有60%",
    "导航系统太蠢了，总是重复扫同一个地方，其他地方完全忽略",
    "花了五千多买的，导航还不如我之前一千块的老款",
    "多楼层地图功能根本不能用，换了楼层就全乱套",
    "禁区设置形同虚设，设了不让进厨房还是照样冲进去",
    "机器人在床底下转了40分钟出不来，最后没电了",
    "每次清扫都要救它五六次，比我自己拖地还累",
    "路径规划太差了，漏扫面积至少三分之一",
    "智能分区功能完全不准，把客厅和餐厅划成了一块",
    "机器人经常在同一个角落反复转圈，就是出不来",
    "导航精度太差，经常从楼梯边缘掉下去",
    "说好的3D避障，结果连拖鞋都避不开",
    "建图速度慢得要死，120平的房子建了半小时还没完成",
    "禁区划了跟没划一样，每次都闯进去",
    "机器人总是卡在门槛上，过不去也不绕路，就在那顶着",
    "每次清扫完地图就变了，分区全乱了，要重新设置",
    "避障太保守了，离障碍物老远就绕开，导致大片区域扫不到",
    "导航芯片明显算力不够，经常卡顿不动",
    "APP上显示的位置和实际位置差了十万八千里",
    "机器人找不到回充的路，每次都在离充电座一米的地方没电",
    "路径规划完全看不懂，明明直线能到的非要绕一大圈",
    "在同一个房间转了20分钟还在原地，导航算法太烂了",
    "机器人总是往死角里钻，进去就出不来",
    "多地图功能就是摆设，切换地图后机器人完全懵了",
    "说好的AI路径规划，实际就是瞎转，没有任何规律",
    "每次清扫路线都不一样，同样的地方有时扫三遍有时一遍都不扫",
    "机器人对透明障碍物完全识别不了，直接撞上去",
    "导航效率太低了，120平要扫3个小时，别人的1小时就搞定",
    "机器人经常在门口徘徊，就是不进去扫",
]

battery = [
    "电池太差了，用了半年就衰减到扫不完一个房间",
    "充了4小时电，扫了20分钟就没电了，什么垃圾",
    "电池续航严重虚标，标称180分钟实际只有60分钟",
    "用了不到一年电池就鼓包了，都不敢用了",
    "充电速度慢得要死，充3小时扫30分钟，这比例也太离谱了",
    "电池续航越来越差，刚买的时候能扫全屋，现在扫一半就没电",
    "回充后续航不续，扫到一半回去充电，充完电不继续扫了",
    "电池完全不经用，120平的房子要分三次才能扫完",
    "充电接触不良，放回充电座经常充不上电",
    "电池衰减太快了，三个月就从180分钟掉到90分钟",
    "充电座识别有问题，经常充不上电，机器人就停在那",
    "续航太短了，扫到一半回充，充完之后忘了刚才扫到哪了",
    "电池完全不耐用，一年不到就要换电池，换电池要400块",
    "充电时间太长了，充4个小时才能用1个小时",
    "机器人经常显示充电中但实际没充进去，浪费一整天",
    "续航虚标严重，宣传说200分钟，实际最多80分钟",
    "电池质量太差，用了8个月就彻底不行了，换新电池又贵",
    "充电座经常断连，机器人充了一晚上结果没充进去",
    "电池不经用，每次扫到一半就低电量回充，根本扫不完",
    "回充后不继续清扫，等于每次只能扫一半",
    "充了一整晚的电，结果只扫了15分钟就提示低电量",
    "电池寿命太短，一年不到续航就只有原来的一半了",
    "充电效率太低，等它充好电我手动都拖完了",
    "电池续航和宣传差太远了，说好的3小时实际1小时",
    "充电接触点容易氧化，经常接触不良充不上电",
]

cleaning = [
    "扫地根本扫不干净，灰尘还在，毛发还缠在滚刷上",
    "拖地功能就是个笑话，水洒得到处都是，还不如我手动拖",
    "吸力太小了，稍微大点的颗粒就吸不进去",
    "拖布根本不转，就是拖着走，跟抹布擦地没区别",
    "边角完全扫不到，墙角一圈全是灰",
    "拖地漏水严重，每次拖完地上全是水渍，干了还有白印",
    "滚刷太容易缠毛发了，每次用完都要手动清理，太麻烦",
    "扫完地还不如没扫，灰尘只是被推到墙角了",
    "拖地功能太鸡肋了，只能喷点水打湿表面，根本擦不干净",
    "吸力严重不足，猫粮都吸不进去，更别说猫砂了",
    "集尘盒太小了，扫一个房间就满了，要不停倒",
    "拖布太薄了，稍微脏一点就黑了，洗也洗不干净",
    "清扫覆盖率太低，很多地方根本扫不到",
    "拖地后地面水痕严重，看起来比没拖还脏",
    "滚刷设计有问题，长发一缠就卡死，每次都要拆开剪",
    "扫地时灰尘飞扬，感觉比扫帚还差",
    "拖地模式下水箱漏水，不拖地的时候也滴答滴答",
    "边刷太软了，墙边的灰尘根本扫不到",
    "吸力模式调到最大也没用，还是吸不干净",
    "拖地效果太差了，油污完全擦不掉，还得自己再擦一遍",
    "自动集尘声音巨大，而且经常堵住集尘口",
    "扫完地地上还有明显灰尘，用纸一擦全是灰",
    "拖布清洗不干净，越拖越脏",
    "边角清扫能力几乎为零，墙角积了一层灰",
    "滚刷被毛发缠住后机器就报错停了，每天都要拆开清理",
    "拖地时水洒得到处都是，木地板都被泡了",
    "吸力衰减严重，用了三个月就明显不如新买的时候",
    "清扫效率太低，同样的面积要扫两遍才勉强干净",
    "拖地后留下明显水渍，干了以后还有白色水印",
    "集尘盒密封不好，灰尘从缝隙漏出来，二次污染",
]

connectivity = [
    "WiFi连接太不稳定了，三天两头断连",
    "APP根本连不上机器人，重置了十几次都没用",
    "每次断电后都要重新配网，太麻烦了",
    "APP上显示离线，但机器人就在那亮着灯，什么鬼",
    "蓝牙和WiFi切换经常出问题，连不上就什么都干不了",
    "远程控制功能就是个摆设，在外面根本连不上",
    "APP功能太简陋了，连定时清扫都设置不了",
    "5G WiFi不支持，只能用2.4G，我家路由器还得专门调",
    "APP经常闪退，设置好的清扫计划全没了",
    "语音控制基本不能用，喊十次能听懂一次就不错了",
    "WiFi模块质量太差，用了一年就彻底连不上了",
    "APP上地图加载不出来，每次都要等半天",
    "每次路由器重启后机器人就断连，要重新配网",
    "APP推送通知太慢了，机器人卡住半小时了才收到提醒",
    "智能家居联动功能根本不能用，说好的支持米家结果是假的",
    "APP上显示的清扫记录和实际完全对不上",
    "配网过程太复杂了，试了十几次才连上",
    "APP更新后反而更难用了，以前的功能都没了",
    "远程启动经常失败，点开始清扫没反应",
    "WiFi信号稍微弱一点就连不上，我家卧室就扫不了",
]

quality = [
    "用了三个月就坏了，电机异响，客服说要返厂维修",
    "外壳做工太粗糙了，接缝处都能看到里面的线",
    "轮子用了半年就掉了，质量太差了",
    "才用了两个月传感器就失灵了，一直报错",
    "水箱漏水，用了几次就发现底座全是水，差点把地板泡了",
    "塑料件质量太差，轻轻一碰就裂了",
    "滚刷轴承生锈了，才用了半年，这防水也太差了",
    "充电触点氧化严重，经常接触不良",
    "机器用了不到一年就彻底罢工了，开机没反应",
    "拖布支架断裂，材质太脆了",
    "边刷掉毛严重，用了两周就秃了",
    "主板烧了，用了才8个月，维修费要600",
    "激光雷达罩子裂了，导航直接废了",
    "底座排水口堵塞，每次都溢水",
    "集尘袋卡扣断了，集尘功能废了",
    "前轮脱落，机器人直接趴窝",
    "尘盒盖子关不严，灰尘到处飞",
    "充电座线太短了，插座远一点就够不着",
    "机器异响严重，像拖拉机一样",
    "用了半年水箱就裂了，水漏了一地",
    "传感器进灰后完全失灵，机器人在楼梯口直接冲下去",
    "橡胶履带断了，换一条要200块",
    "基站清洗功能坏了，拖布越洗越脏",
    "机器经常报假错误，明明没问题非要我检查",
    "按键手感太差，按了没反应，要使劲按才行",
]

service = [
    "客服态度太差了，问了半天给不出解决方案",
    "报修后等了两周才有人来，期间机器人完全不能用",
    "保修期内维修还要收费，说什么人为损坏，明明是质量问题",
    "客服电话永远打不通，在线客服排队两小时",
    "返厂维修回来还是坏的，又寄回去修，来来回回一个月",
    "配件太贵了，换个滚刷要200，换个电池要400",
    "售后说过了保修期不修，才超了10天就不给修了",
    "客服只会说重启试试，重启了八百遍了还是不行",
    "维修周期太长了，寄回去三周了还没修好",
    "换新机也是坏的，连续换了三台都有问题",
    "客服推来推去，线上说找线下，线下说找线上",
    "投诉了也没用，就给个优惠券打发你",
    "维修费用比新机还贵，不如直接扔了",
    "售后电话打不通，邮件三天才回，效率太低了",
    "说好的上门维修，结果让我自己寄回去",
    "客服完全不懂技术，问什么都是让我重启重置",
    "换货等了一个月，新货还是有问题",
    "保修条款全是霸王条款，什么都是消费者的问题",
    "售后网点太少，最近的在200公里外",
    "客服承诺的回电从来没打过，等了一周也没人联系",
    "维修完用了一周又坏了，同样的故障反复出现",
    "客服态度敷衍，说这是正常现象，明明就是坏了",
    "配件缺货，等了两个月还没到",
    "售后说不在保修范围，什么都在保修范围外",
    "投诉到12315才给处理，不投诉就不管",
]

mopping = [
    "拖地功能完全不能用，水洒得到处都是",
    "拖布洗不干净，越拖越脏，还不如手动拖",
    "基站清洗拖布效果太差，拖布上还有明显的污渍",
    "自动上下水功能装不了，每次要手动加水倒水太麻烦",
    "拖地时水箱漏水，木地板都被泡变形了",
    "拖布烘干功能太慢了，半天都干不了，发霉发臭",
    "拖地模式噪音太大，比扫地还吵",
    "基站清洗槽太脏了，每次清洗拖布反而把拖布弄脏",
    "拖地后地面水渍明显，干了还有白色水印",
    "拖布太薄了，稍微脏一点就黑了",
    "自动添加清洁液功能根本不好使，加了跟没加一样",
    "基站排水口经常堵塞，污水溢出来",
    "拖地路径规划不合理，湿拖布在已经拖过的地方反复走",
    "拖地力度太轻了，地上的污渍完全擦不掉",
    "基站清洗拖布的声音太大了，像在洗衣服",
    "拖布安装拆卸太麻烦了，每次都要拧螺丝",
    "水箱容量太小，拖一个房间就要加水",
    "拖地后地面太湿了，走路会打滑",
    "基站自动清洗功能经常报错，说清洗盘异常",
    "拖布用了两个月就变形了，拖不干净了",
    "拖地时机器人速度太快，水都来不及擦就过去了",
    "基站污水盒太小，拖两个房间就要倒污水",
    "拖地模式耗电太快，扫拖一遍都撑不住",
    "拖布烘干后还是潮的，放久了有异味",
    "基站清洗不彻底，拖布上有残留的毛发和灰尘",
]

noise = [
    "噪音太大了，根本没法在它工作的时候待在家里",
    "集尘的时候声音像飞机起飞，吓死人了",
    "扫地模式噪音还可以，拖地模式噪音太大了",
    "自动集尘声音太大了，每次集尘都被吓一跳",
    "晚上根本不敢用，噪音太大影响邻居",
    "比传统吸尘器还吵，说好的静音呢？",
    "基站工作的时候噪音也很大，放在客厅根本受不了",
    "噪音分贝严重虚标，标称55dB实际至少70dB",
    "边刷碰到墙壁的声音特别刺耳，砰砰砰的",
    "回充的时候电机声音突然变大，像拖拉机",
    "集尘站工作的时候整栋楼都能听到",
    "半夜自动启动清扫，把我吓醒了，噪音太大了",
    "拖地时水泵工作的声音很吵，嗡嗡嗡的",
    "建图的时候噪音特别大，持续半小时受不了",
    "噪音大到我家猫都吓跑了，每次清扫都躲起来",
    "正常清扫模式噪音还可以，强力模式简直不能忍",
    "基站清洗拖布的时候声音特别大，像洗衣机脱水",
    "机器人报错时的提示音太刺耳了，而且关不掉",
    "充电的时候也有轻微噪音，放在卧室影响睡眠",
    "集尘声音太突然了，没有任何预警就轰的一声",
]

price = [
    "五千多买的，用了半年就坏了，太不值了",
    "性价比太低了，这价位的功能两千块的也有",
    "花了一万多买的顶配，结果跟三千块的没区别",
    "太贵了，完全不值这个价，后悔死了",
    "配件价格太离谱了，换个滤网要150，换个滚刷要200",
    "维修费用比新机还贵，不如直接买新的",
    "这价格买个传统吸尘器+拖把，效果还好十倍",
    "花六千买了个祖宗回来，天天伺候它",
    "溢价太严重了，功能配不上这个价格",
    "买的时候觉得贵点没关系，用了才知道是真不值",
    "耗材成本太高了，一年下来配件费都要大几百",
    "同价位别的品牌功能更多，买这个真的后悔",
    "降价太快了，买了两个月就降了一千，血亏",
    "这质量卖这个价格，简直是抢钱",
    "花四千多买的，还不如同事一千五的好用",
    "保修期太短了，才一年，过了保修就各种坏",
    "维修费太贵了，换个主板要一千多",
    "买完就后悔，这价格完全可以买更好的品牌",
    "功能都是噱头，核心体验配不上这个价格",
    "花大价钱买了个摆设，还不如手动打扫",
]

smart = [
    "AI避障就是个噱头，连鞋子都避不开",
    "说好的智能规划路线，实际就是随机乱转",
    "语音控制识别率太低了，说了十遍才听懂一次",
    "APP功能太简陋了，连基本的分区清扫都设置不好",
    "智能推荐清扫模式根本不准，每次都推荐错的",
    "AI识别障碍物完全不行，数据线一缠就卡死",
    "智能定时功能经常失效，设了7点启动结果9点才动",
    "说好的3D地图，实际就是2D平面图加了个噱头标签",
    "智能避障太保守了，离障碍物老远就绕开，大面积漏扫",
    "AI脏污识别根本不存在，不管脏不脏都扫一样的时间",
    "APP地图编辑功能太难用了，划个禁区要试好几次",
    "智能回充经常失败，到了充电座旁边就是对不准",
    "AI场景识别就是个笑话，把地毯识别成了障碍物",
    "APP推送通知延迟严重，机器人卡住半小时了才通知我",
    "智能联动功能完全不能用，说好的米家支持是假的",
    "语音助手经常误触发，看电视时突然开始清扫",
    "AI识别宠物粪便功能完全没用，照样碾过去",
    "APP上显示的清扫进度和实际完全对不上",
    "智能推荐清扫时间太蠢了，推荐我凌晨3点清扫",
    "AI避障把黑色地毯识别成了悬崖，死活不上去",
]

mapping = [
    "建图速度太慢了，120平的房子建了40分钟",
    "地图总是丢失，每周都要重新建图",
    "多楼层地图功能根本不能用，换楼层就全乱",
    "地图精度太差，和实际房间布局差了十万八千里",
    "每次清扫完地图就变了，分区全乱了",
    "地图编辑功能太难用了，划个禁区要试好几次",
    "地图上的房间面积和实际面积差了30%",
    "建图的时候经常卡死，要重启好几次才能建完",
    "地图保存不了，每次打开APP都要重新加载",
    "多地图切换后机器人完全懵了，不知道自己在哪",
    "地图更新太频繁了，每次家具挪一下就要重新建图",
    "地图上的家具位置和实际位置对不上",
    "建图时机器人经常迷路，建出来的地图是乱的",
    "地图缩放功能太难用了，根本看不清细节",
    "地图上的清扫记录和实际路线完全对不上",
    "建图时经常把一个房间识别成两个",
    "地图上的禁区经常自动消失，要重新设置",
    "建图时机器人总是漏掉一些区域",
    "地图加载速度太慢了，每次打开要等10秒",
    "地图上显示已清扫的区域实际根本没扫到",
]

dock = [
    "基站排水口经常堵塞，污水溢出来",
    "自动集尘声音太大了，像飞机起飞",
    "基站清洗拖布效果太差，拖布上还有污渍",
    "基站经常报错，说清洗盘异常，修了三次还是不行",
    "基站和机器人连接不稳定，经常断连",
    "集尘袋容量太小，两周就满了，换一个要50块",
    "基站自清洁功能就是个笑话，基站本身就很脏",
    "基站占地方太大了，小户型根本放不下",
    "基站加水倒水太麻烦了，没有自动上下水",
    "基站噪音太大，放在客厅根本受不了",
    "基站固件更新后反而更难用了，经常报错",
    "基站清洗槽发霉发臭，清理起来特别麻烦",
    "基站和机器人对准困难，经常充不上电",
    "基站集尘功能经常卡住，灰尘堵在管道里",
    "基站水箱太小，拖两个房间就要加水",
    "基站工作时异味很重，放在客厅很影响体验",
    "基站底座积水严重，时间长了发霉",
    "基站自动添加清洁液功能不好使",
    "基站烘干拖布太慢了，4个小时都干不了",
    "基站清洗拖布时水花四溅，周围地面都是水",
]

stuck = [
    "总是卡在沙发底下出不来，一天要救好几次",
    "电线一缠就死，每次都要手动解开",
    "卡在门槛上过不去，也不报错就在那顶着",
    "被窗帘缠住了，电机烧了，维修费500",
    "卡在床底和墙的缝隙里，出不来也退不回去",
    "袜子吸进去就卡死，每次都要拆开取",
    "卡在椅子腿中间出不来，一直原地打转",
    "地毯边缘总是卡住，上不去也下不来",
    "充电线缠住滚刷，机器直接报错停了",
    "卡在卫生间门槛上，进不去也退不出",
    "宠物玩具吸进去卡死了，滚刷转不动",
    "卡在茶几和沙发之间的缝隙，每次都要搬家具救它",
    "拖鞋卡在机器底下，推着拖鞋走也不报错",
    "厨房地垫边缘卡住，每次到这就停",
    "被绳子缠住了轮子，完全动不了",
    "卡在楼梯边缘，差点掉下去",
    "餐桌底下的横梁卡住机器人，每次都卡",
    "浴室门口的挡水条过不去，每次都卡在那",
    "孩子的乐高散在地上，机器人碾过去卡住了",
    "窗帘下摆卷进滚刷，机器直接停了",
]

short_neg = [
    "垃圾，别买",
    "太差了",
    "后悔买了",
    "千万别买",
    "浪费钱",
    "不推荐",
    "质量太差",
    "经常卡住",
    "扫不干净",
    "总是断连",
    "噪音太大",
    "电池太差",
    "导航太烂",
    "客服不行",
    "拖地漏水",
    "用不了多久就坏了",
    "虚标严重",
    "避障不行",
    "地图总丢",
    "不值这个价",
    "太失望了",
    "完全不好用",
    "买来就后悔",
    "问题太多了",
    "修了好几次还是不行",
]

mixed = [
    "好用是好用，就是偶尔会迷路，还能接受吧",
    "扫地还行，拖地就别指望了，水洒得到处都是",
    "前三个月很好用，后来就开始各种出问题",
    "导航还行，但是电池太差了，扫不完就要充电",
    "吸力够用，就是噪音太大了，受不了",
    "APP设计不错，但经常断连，体验很差",
    "外观好看，但功能配不上这个价格",
    "扫地功能可以，拖地功能就是个摆设",
    "安静的时候挺好，集尘的时候吵死了",
    "建图很快，但地图经常丢失，要重新建",
    "避障有时候很灵，有时候直接撞上去，不稳定",
    "充电速度可以，但续航太短了",
    "客服回复挺快的，但解决不了问题",
    "机器本身还行，基站太占地方了",
    "单扫模式不错，扫拖模式各种报错",
    "刚买来很惊艳，用了两个月就各种小毛病",
    "在硬地板上还行，地毯上就歇菜",
    "定时清扫功能好用，但经常连不上WiFi执行不了",
    "自动集尘很方便，但声音太大像爆炸",
    "机器清扫能力可以，但APP太难用了",
    "整体还行，就是边角扫不到，还得手动补",
    "机器人质量可以，基站质量太差了",
    "清扫效果满意，但耗材太贵了用不起",
    "功能挺多的，但每个都只做到60分",
    "外观设计好看，但实用性太差了",
]

complaint_long = [
    "我于2024年3月花了3600元在京东买了一台扫地机器人，满怀期待地希望能从繁琐的家务中解脱出来。结果首台机器刚送达，安装师傅就发现它无法完成建图功能，当场就打包返厂了。第二台、第三台机器接连出现拖地漏水、指令失灵等不同问题。当第四台新机送达时，短暂使用后依然陷入了故障循环。四台全新的机器，没有一台能正常工作，这已经超出了偶发问题的范畴，而是产品本身存在严重的质量缺陷。联系售后，得到的答复是已过换货时效，仅同意维修。维修后的机器用了不到三个月又彻底瘫痪了。客服提出赠送耗材作为补偿，机器本身都无法使用，送再多耗材又有什么意义？",
    "买了这台五千多的扫地机器人，用了不到一年就从帮忙做家务的变成了定时闹钟。第一次开机就在瓷砖地上留下一道道划痕，水箱里的水洒得到处都是。宣传页上写着自动补水拖地，实际上每天要手动加清水倒污水，每次清扫前后各花十分钟准备和收拾，比直接拿拖把干一遍还麻烦。电量不够用，120平的房子扫到一半就得回去充电，充两个小时再继续，整个过程要四五个小时。它还很容易卡住，在沙发腿、充电线或者拖鞋旁边就停住不动，每次打扫平均要救它五六次。避障功能更奇怪，看到障碍物不是绕过去而是直接放弃那片区域，清洁覆盖率只有65%左右。最后实在受不了，把充电底座也塞进纸箱回收了。",
    "我花了1600美元买了iRobot Roomba和清洁基站，从第一天起就问题不断。不是无法启动，就是连不上WiFi，或者反复提示清空集尘盒（清洁基站应该自动做的）。我发了两次邮件列出所有问题，没人回复。最后机器彻底罢工了，他们换了清洁基站因为还在保修期内。四个月后同样的问题又出现了，充电触点熔在一起导致无法充电。他们拒绝更换，声称我没有做好维护。维护要求就是擦一擦，我用专用清洁布和泡沫都擦了。他们花了四个月才回复我然后拒绝处理。我以前最早期的Roomba很好用，现在他们只是在吃老本。产品质量不达标，客服更差。",
    "这台扫地机器人从买回来就有问题。安装一周后就出现异响，客服说是滚刷问题，按他们教的方法清理了还是不行。地面拖地水痕严重，打扫完还不如没打扫的时候。拖地的边刷有一边凸起来了，扫地时那边的拖布是拖着地走的。机器经常出异常报告，让它在家自己拖地，没有一次完整拖下来的。连几粒狗粮都扫不进去，扫的时候严重异响。产品存在严重的质量问题，我要求退货退款。售后特别差，客服像机器人一样，让他们发SN码然后就石沉大海。本来只想换新，现在一门心思要退货。",
    "用了170天只工作了8次，累计时长12.9小时。10月8日机器首次罢工，基站无法排水，返厂维修。10月25日维修机寄回当天，机器人再次卡死、排水依旧失灵，更开始疯狂漏水。一个用了不到13小时的产品，返修回来当天就坏了！提出换货，客服只给出继续维修的敷衍方案。12.9小时坏2次，照这个频次，两年质保期后岂不是要被修哭？售后特别垃圾，客服的傲慢与表演式售后让我彻底心寒。他们让我发SN码，然后就石沉大海。目前已向315和12345进行了投诉。",
    "我买了iRobot Roomba J8+，专门因为它宣传能避开宠物排泄物。这是这个型号的主要卖点，也是我付高价的原因。结果产品彻底失败了，我的Roomba J8+直接碾过了狗屎，把粪便涂抹到了整个房子的地板上。清理花了三个小时，地毯不得不扔掉。联系客服，他们说我的地面环境不在保证范围内。花了一千多美元买个给我制造更多家务的机器，太荒谬了。",
    "这台机器买来用了三个月，先是滚刷异响，换了滚刷后开始频繁断连。每次断连后地图就丢了，要重新建图。建图要半小时，建完图扫了两个房间又断连。如此循环，根本没法正常使用。联系客服，客服让我重启路由器、重置机器人、更新固件，全试了还是不行。最后客服说可能是WiFi模块坏了，要返厂维修。返厂两周，寄回来用了三天又断连了。再联系客服，又说让我重置。我重置了不下二十次了，问题根本没解决。这台机器就是个半成品，根本没做好就拿出来卖了。",
    "买之前看了很多好评，以为真的能解放双手。结果用了一个月，发现完全不是那么回事。首先它经常卡在家具底下出不来，平均每次清扫要救它三四次。其次拖地功能太鸡肋了，只能把地面弄湿，根本擦不掉任何污渍。最让我崩溃的是自动集尘功能，声音大得像飞机起飞，每次集尘都被吓一跳，而且集尘袋两周就满了，换一个要50块。算下来一年的耗材费用就要大几百。花了五千多买个需要不停伺候的机器，还不如花五百买个好拖把。",
]

real_amazon = [
    "This robot vacuum is a complete waste of money. It got stuck under my couch every single time I ran it. Navigation is terrible.",
    "Stopped working after 3 months. Customer service was no help at all. They kept telling me to reset it. I reset it 20 times!",
    "The mapping feature is useless. Every time I turn it on, it creates a different map. Can't even clean my living room properly.",
    "Battery life is a joke. Claims 180 minutes but barely lasts 60. And it takes 4 hours to charge. Unacceptable.",
    "Don't waste your money. This thing can't even avoid a pair of shoes on the floor. AI obstacle avoidance is a lie.",
    "The mopping function is garbage. It just smears water around. My floors look worse after it mops than before.",
    "WiFi keeps disconnecting. I have to re-pair it every other day. What's the point of a smart vacuum if it can't stay connected?",
    "Got this for Christmas and it's already broken. The front wheel fell off after 2 months. Cheap plastic parts.",
    "The app is useless. Half the time it shows the robot as offline when it's sitting right next to the router.",
    "Noise level is ridiculous. Sounds like a jet engine when it self-empties. Can't run it when anyone is home.",
    "I've had to rescue this vacuum from under my furniture more times than I can count. Not smart at all.",
    "The dust bin is way too small. Have to empty it after every room. My old vacuum was better than this.",
    "Customer service is terrible. Been waiting 3 weeks for a replacement part. Still nothing.",
    "It keeps missing entire rooms. I have a simple floor plan and it still can't figure out where to go.",
    "The self-cleaning base is always clogging. Had to take it apart 5 times already. Not worth the hassle.",
    "Worked great for the first month, then everything went downhill. Now it just spins in circles.",
    "The edge cleaning is non-existent. There's a 2-inch strip of dust along every wall.",
    "I regret buying this. My $150 stick vacuum does a better job than this $800 robot.",
    "The virtual wall feature doesn't work at all. It goes wherever it wants regardless of boundaries.",
    "Charging contacts corroded after 6 months. Now it won't charge at all. Cheap materials.",
    "This is my third replacement unit and it still has the same problems. Quality control is nonexistent.",
    "The mopping pad is too thin and gets dirty instantly. Then it just spreads dirt around. Useless.",
    "It ran over dog poop and smeared it everywhere. Three hours of cleaning. This is the opposite of helpful.",
    "The app keeps crashing. Lost all my room settings twice. Have to remap everything.",
    "Way too expensive for what you get. My friend's $200 robot works better than this $600 one.",
    "The roller brush gets tangled with hair every single time. Have to cut it out with scissors. Design flaw.",
    "It can't find its docking station half the time. Just dies in the middle of the floor.",
    "The water tank leaks. Found a puddle under the dock. Could have damaged my hardwood floors.",
    "Firmware update broke it. Now it won't connect to WiFi at all. Support says they're working on it. Been 2 months.",
    "The suction power is weak. Can't even pick up rice grains. What's the point?",
]

sources_cn = ["京东", "天猫", "淘宝", "拼多多", "什么值得买", "小红书", "黑猫投诉", "微博", "抖音", "知乎"]
sources_en = ["Amazon", "Best Buy", "Walmart", "Reddit", "Consumer Reports", "BBB", "ProductReview"]
brands = ["科沃斯", "追觅", "石头", "云鲸", "iRobot", "Roborock", "Shark", "Dyson", "小米", "美的"]

all_categories = {
    "导航避障": navigation,
    "电池续航": battery,
    "清扫效果": cleaning,
    "连接问题": connectivity,
    "质量问题": quality,
    "售后服务": service,
    "拖地功能": mopping,
    "噪音问题": noise,
    "性价比": price,
    "智能功能": smart,
    "地图建图": mapping,
    "基站问题": dock,
    "卡住困住": stuck,
    "短评": short_neg,
    "混合评价": mixed,
    "长篇投诉": complaint_long,
    "英文评论": real_amazon,
}

review_id = 1
for cat_name, cat_reviews in all_categories.items():
    for text in cat_reviews:
        is_en = any(c.isascii() and c.isalpha() for c in text[:5])
        source = random.choice(sources_en if is_en else sources_cn)
        brand = random.choice(brands)
        
        if cat_name == "短评":
            sentiment = "负向"
            priority = random.choice(["中", "低"])
        elif cat_name == "混合评价":
            sentiment = "负向"
            priority = "中"
        elif cat_name == "长篇投诉":
            sentiment = "负向"
            priority = "高"
        elif cat_name in ["质量问题", "售后服务"]:
            sentiment = "负向"
            priority = random.choice(["高", "中"])
        else:
            sentiment = "负向"
            priority = random.choice(["高", "中", "低"])
        
        reviews.append({
            "id": f"R{review_id:03d}",
            "text": text,
            "source": source,
            "brand": brand,
            "category": cat_name,
            "expected_sentiment": sentiment,
            "expected_priority": priority,
        })
        review_id += 1

while len(reviews) < 500:
    cat_name = random.choice(list(all_categories.keys()))
    cat_reviews = all_categories[cat_name]
    base_text = random.choice(cat_reviews)
    
    prefixes = ["又", "还是", "真的", "实在", "太", "也是", "还是说"]
    suffixes = ["，太失望了", "，后悔买了", "，不推荐", "，千万别买", "，浪费钱", ""]
    
    if any(c.isascii() and c.isalpha() for c in base_text[:5]):
        new_text = base_text
    else:
        new_text = random.choice(prefixes) + base_text + random.choice(suffixes)
    
    is_en = any(c.isascii() and c.isalpha() for c in new_text[:5])
    source = random.choice(sources_en if is_en else sources_cn)
    brand = random.choice(brands)
    
    sentiment = "负向"
    if cat_name in ["质量问题", "长篇投诉"]:
        priority = random.choice(["高", "中"])
    elif cat_name == "短评":
        priority = random.choice(["中", "低"])
    else:
        priority = random.choice(["高", "中", "低"])
    
    reviews.append({
        "id": f"R{review_id:03d}",
        "text": new_text,
        "source": source,
        "brand": brand,
        "category": cat_name,
        "expected_sentiment": sentiment,
        "expected_priority": priority,
    })
    review_id += 1

random.shuffle(reviews)
for i, r in enumerate(reviews):
    r["id"] = f"R{i+1:03d}"

output_dir = r"d:\产品分析\SpecMark\tests"
os.makedirs(output_dir, exist_ok=True)

json_path = os.path.join(output_dir, "robot_vacuum_reviews_500.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)

csv_path = os.path.join(output_dir, "robot_vacuum_reviews_500.csv")
with open(csv_path, "w", encoding="utf-8-sig") as f:
    headers = ["id", "text", "source", "brand", "category", "expected_sentiment", "expected_priority"]
    f.write(",".join(headers) + "\n")
    for r in reviews:
        text_clean = r["text"].replace('"', '""').replace("\n", " ")
        line = f'{r["id"]},"{text_clean}",{r["source"]},{r["brand"]},{r["category"]},{r["expected_sentiment"]},{r["expected_priority"]}'
        f.write(line + "\n")

print(f"生成完成！共 {len(reviews)} 条评论")
print(f"JSON: {json_path}")
print(f"CSV:  {csv_path}")

cat_counts = {}
for r in reviews:
    cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1
print("\n分类统计：")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}条")
