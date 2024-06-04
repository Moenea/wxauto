# -*- coding: utf-8 -*-
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, NavigableString
import asyncio
import pandas as pd
import json
from datetime import datetime, timedelta
from cls_jiahong_utils import *


# # 读取存储的.csv文件
# df = pd.read_csv(file_destination, encoding='utf-8')

# # 将 JSON 字符串转换回列表
# df['Text'] = df['Text'].apply(json.loads)

# # 每个元素表示一行
# for i in range(df.shape[0]):
#     time = df.iloc[i,1]
#     data_list = df.iloc[i,0]
#     text = time+"\n\n"+"\n\n".join(data_list)
#     print(text)
#     print('\n\n')

async def main():
    file_destination = './news_data/cls_jiahong.csv'
    await fetch_cls_content(file_destination)

# 运行异步函数
asyncio.run(main())

