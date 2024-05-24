import pandas as pd
import asyncio
from xueqiu_utils import fetch_weibo_content


async def main():
    url = 'https://xueqiu.com/u/3697768583'
    file_destination = './news_data/xueqiu_fudanchengzicheng.csv'
    await fetch_weibo_content(url, file_destination)

# 运行异步函数
asyncio.run(main())

# file_destination = './news_data/xueqiu_fudanchengzicheng.csv'
# # 读取存储的.csv文件
# df = pd.read_csv(file_destination, encoding='utf-8')
# df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
# # 每个元素表示一行
# for i in range(df.shape[0]):
#     text = str(df.iloc[i,1])+"\n\n"+df.iloc[i,0]
#     print(text)
#     print('\n')