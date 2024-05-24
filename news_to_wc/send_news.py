from wxauto import WeChat
from time import sleep
from update_news import update_news


wx = WeChat()

# 发送消息
# who = '文件传输助手'
who = 'xxxxIe'

news_name_list = ['cls_jiahong', 'weibo_aizaibingchuan', 'weibo_tangshuzhuren', 'weibo_xianglong18duan', 'xueqiu_fudanchengzicheng', 'xueqiu_lunhui666', 'xueqiu_Nzhouer']

while True:
    print('Fetching News ...')
    for news_name in news_name_list:
        text_list = update_news(news_name)
        for text in text_list:
            wx.SendMsg(text, who)
            sleep(3)
        sleep(5)
