import pandas as pd
import asyncio
from weibo_utils import fetch_weibo_content


async def main():
    url = 'https://m.weibo.cn/u/2014433131'
    file_destination = './news_data/weibo_tangshuzhuren.csv'
    await fetch_weibo_content(url, file_destination)

# 运行异步函数
asyncio.run(main())


# file_destination = './news_data/weibo_tangshuzhuren.csv'
# # 读取存储的.csv文件
# df = pd.read_csv(file_destination, encoding='utf-8')
# # 每个元素表示一行
# for i in range(df.shape[0]):
#     text = df.iloc[i,1]+"\n\n"+df.iloc[i,0]
#     print(text)
#     print('\n')