# -*- coding: utf-8 -*-
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, NavigableString
import asyncio
import pandas as pd
import json
from datetime import datetime, timedelta
import aiohttp
import os


def is_in_directory(file_path, directory):
    # 获取文件路径和目录的绝对路径
    file_path = os.path.abspath(file_path)
    directory = os.path.abspath(directory)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return False
    
    # 判断文件路径是否以目录路径开头
    return os.path.commonpath([file_path, directory]) == directory

async def download_image(url, file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                # 确保文件夹存在
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(content)
                # print(f"Image downloaded and saved as {file_path}")
            else:
                print(f"Failed to download image, status code: {response.status}")

# 定义一个函数将字符串时间转换为 datetime 对象，适用于财联社数据，因为时间是 %H:%M:%S 格式
def convert_time(time_str):
    # 获取当前日期和时间
    now = datetime.now()
    time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
    time_today = datetime.combine(now.date(), time_obj)
    if time_today > now:
        # 如果时间超过当前时间，则说明是昨天的时间
        time_today -= timedelta(days=1)
    return time_today

async def fetch_cls_content(file_destination):
    async with async_playwright() as p:
        # 创建一个浏览器实例
        browser = await p.chromium.launch()

        # 创建一个新的页面
        page = await browser.new_page()

        # 打开网页
        await page.goto('https://www.cls.cn/telegraph')

        # 点击文本为“加红”的h3元素
        await page.click('text="加红"')

        # 等待页面加载
        await asyncio.sleep(1)

        # 获取页面内容
        content = await page.content()

        # 使用BeautifulSoup解析
        soup = BeautifulSoup(content, 'html.parser')

        # 找到class为“f-l content-left”的div元素
        target_div = soup.find('div', {'class': 'f-l content-left'})

        # 在target_div中找到所有的div元素
        divs = target_div.find_all('div', recursive=True)

        time_list = []
        content_text_list = []
        pic_list = []
        for div in divs:
            # 找到div中的所有直接子元素
            children = [child for child in div.children]

            # 检测是否存在class为 m-t-15 的 div，如有则说明有图片
            for child in children:
                if child.name == 'div' and 'm-t-15' in child.get('class', []):
                    # 使用 Playwright 的 query_selector 查找对应的 img 元素
                    img_ele = child.find('img')
                    if img_ele:
                        # 获取图片 src 并下载
                        img_src = img_ele.get('src')
                        large_img_src = img_src.split('?')[0]

                        pic_id = convert_time(time_list[-1]).strftime("%Y%m%d%H%M%S")
                        file_path = './news_pic/cls_' + pic_id + '_image.png'

                        if is_in_directory(file_path, file_path.split('/')[0]+'/'+file_path.split('/')[1]):
                            pass
                        else:
                            await download_image(large_img_src, file_path)
                    else:
                        print("No img element found in div with class 'm-t-15'.")
                    break
            
            # 检查直接子元素的数量，抓取文本信息
            if len(children) == 2 and children[0].name=='span' and children[1].name=='span':
                time = children[0].text
                if time != '':
                    time_list.append(time)
                    try:
                        _a = file_path
                    except:
                        file_path = None
                    if file_path:
                        pic_list.append(file_path)
                        file_path = None
                    else:
                        pic_list.append('No_Pic')
                
                # 找到第二个span中的所有div元素
                divs_in_span = children[1].find_all('div', recursive=False)
                
                _temp_content_text = []
                # 检查div的数量
                if len(divs_in_span) == 1:
                    _temp_content_text.append(divs_in_span[0].text)
                elif len(divs_in_span) > 1:
                    for div_in_span in divs_in_span:
                        # 打印div元素本身的文本
                        for child in div_in_span.children:
                            if isinstance(child, NavigableString):
                                _temp_content_text.append(str(child))
                            elif child.name == 'strong':
                                _temp_content_text.append(child.string)
                if len(_temp_content_text) != 0:
                    content_text_list.append(json.dumps(_temp_content_text, ensure_ascii=False))  # 确保不转义中文字符




        content_text_list = [e.replace('展开收起','') for e in content_text_list]

        # 要写入的数据（存储为JSON格式）
        data = {
            'Text': content_text_list,
            'Time': time_list,
            'Pic': pic_list
        }

        df = pd.DataFrame(data)

        # 应用转换函数
        df['Time'] = df['Time'].apply(convert_time)

        # 读取已有的csv文件，确定要更新的数据，drop掉重复的数据
        try:
            # 读取存储的.csv文件
            df_stored = pd.read_csv(file_destination, encoding='utf-8')
            time_series = df_stored['Time'].values.tolist()
        except:
            time_series = []

        # 进行drop操作
        for i,e in enumerate(df['Time']):
            if str(e) in time_series:
                df.drop(i, inplace=True)

        # 新数据与原数据合并
        if len(time_series) != 0:
            df = pd.concat([df, df_stored], axis=0, ignore_index=True)

        # 再次检查Text列是否有重复，有则删去，保留原始的哪一个row（那是“分钟前”计算的，更加准确）
        df.drop_duplicates(subset='Text', keep='last', inplace=True)

        # 写入CSV文件
        df.to_csv(file_destination, index=False, encoding='utf-8')

        # 关闭浏览器
        await browser.close()

# # 运行异步任务
# asyncio.run(main())
