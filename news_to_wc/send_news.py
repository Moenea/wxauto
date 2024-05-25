from wxauto import WeChat
from time import sleep
from update_news import update_news
import warnings
warnings.filterwarnings("ignore")

wx = WeChat()

# 发送消息
# who = '文件传输助手'
who_list = ['xxxxIe', 'Yango']

news_name_list = ['cls_jiahong', 'weibo_aizaibingchuan', 'weibo_tangshuzhuren', 'weibo_xianglong18duan', 'xueqiu_fudanchengzicheng', 'xueqiu_lunhui666', 'xueqiu_Nzhouer']

try:
    while True:
        print('Fetching News ...')
        for news_name in news_name_list:
            text_list = update_news(news_name)
            for who in who_list:
                for text in text_list:
                    wx.SendMsg(text, who)
                    sleep(2)
            sleep(2)
except KeyboardInterrupt:
    print('Exit Fetching ...')
