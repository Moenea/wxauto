from wxauto import WeChat
from time import sleep
from update_news import update_news
import warnings
import concurrent.futures

warnings.filterwarnings("ignore")

wx = WeChat()

# 发送消息
# who = '文件传输助手'
# who_list = ['xxxxIe', 'Yango']
who_list = ['xxxxIe']

news_name_list = ['cls_jiahong', 'weibo_aizaibingchuan', 'weibo_tangshuzhuren', 'weibo_xianglong18duan', 'xueqiu_fudanchengzicheng', 'xueqiu_Nzhouer'] # 删去了 雪球-轮回666
news_name_list = ['weibo_xianglong18duan', 'xueqiu_fudanchengzicheng']
resouce_name = {
    'cls_jiahong': '财联社-加红',
    'weibo_aizaibingchuan': '微博-爱在冰川',
    'weibo_tangshuzhuren': '微博-唐史主任司马迁',
    'weibo_xianglong18duan': '微博-翔龙十八段',
    'xueqiu_fudanchengzicheng': '雪球-复旦橙子橙',
    'xueqiu_lunhui666': '雪球-轮回666',
    'xueqiu_Nzhouer': '雪球-N周二'
}

def fetch_and_send_news(news_name):
    text_list, pic_list = update_news(news_name, resouce_name[news_name])
    for who in who_list:
        for ind, text in enumerate(text_list):
            wx.SendMsg(text, who)
            if pic_list[ind] != 'No_Pic': # 文字同时有图片
                wx.SendFiles(pic_list[ind], who)
                sleep(1)

try:
    while True:
        print('Fetching News ...')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(fetch_and_send_news, news_name_list)
        sleep(10)
except KeyboardInterrupt:
    print('Exit Fetching ...')
