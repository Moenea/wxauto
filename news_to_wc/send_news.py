from wxauto import WeChat
from time import sleep
from update_news import update_news
import warnings
warnings.filterwarnings("ignore")

wx = WeChat()

# 发送消息
# who = '文件传输助手'
who_list = ['xxxxIe', 'Yango']

news_name_list = ['cls_jiahong', 'weibo_aizaibingchuan', 'weibo_tangshuzhuren', 'weibo_xianglong18duan', 'xueqiu_fudanchengzicheng', 'xueqiu_Nzhouer'] # 删去了 雪球-轮回666
resouce_name = {'cls_jiahong':'财联社-加红', 
                'weibo_aizaibingchuan':'微博-爱在冰川', 'weibo_tangshuzhuren':'微博-唐史主任司马迁', 'weibo_xianglong18duan':'微博-翔龙十八段', 
                'xueqiu_fudanchengzicheng':'雪球-复旦橙子橙', 'xueqiu_lunhui666':'雪球-轮回666', 'xueqiu_Nzhouer':'雪球-N周二'}

try:
    while True:
        print('Fetching News ...')
        for news_name in news_name_list:
            text_list = update_news(news_name, resouce_name[news_name])
            for who in who_list:
                for text in text_list:
                    wx.SendMsg(text, who)
                    sleep(2)
            sleep(2)
        sleep(300)
except KeyboardInterrupt:
    print('Exit Fetching ...')
