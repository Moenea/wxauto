import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd


# 定义一个函数将字符串时间转换为 datetime 对象，适用于微博数据，因为时间是 %m-%d %H:%M 格式
def convert_time(time_str):
    # 当前时间
    now = datetime.now()

    if "昨天" in time_str:
        yesterday = now-timedelta(days=1)
        time_str = time_str.replace("昨天", str(yesterday.month)+'-'+str(yesterday.day))

    # 获取当前年份
    current_year = now.year

    # 构建新的日期字符串，包含当前年份
    new_date_string = f"{current_year}-{time_str}"

    # 定义日期格式
    date_format = "%Y-%m-%d %H:%M"

    time_obj = datetime.strptime(new_date_string, date_format)
    return time_obj

async def fetch_weibo_content(url, file_destination):
    async with async_playwright() as p:
        # 创建一个浏览器实例
        browser = await p.chromium.launch()

        # 创建一个新的页面
        page = await browser.new_page()

        # 打开页面
        await page.goto(url)

        # 等待页面加载
        await asyncio.sleep(0.25)

        # 找到所有class为"weibo-og"的div元素
        elements = await page.query_selector_all('div.weibo-og') # 最后一个元素显示有异常
        elements = elements[:-1]

        # threshold = 25
        # while len(elements) < threshold:
        #     # 模拟滚动到页面底部
        #     await page.keyboard.press('End')
        #     await asyncio.sleep(0.25)  # 等待新的元素加载
        #     elements = await page.query_selector_all("div.weibo-og")
        # print(len(elements))

        time_list = []
        content_text_list = []
        for index, element in enumerate(elements):
            # 获取元素的文本
            element_text = await element.text_content()

            # 点击div元素，进入对应div页面
            await page.click(f'div.weibo-og:has-text("{element_text}")')

            # 等待新页面加载
            await asyncio.sleep(0.25)

            # Post Publish time
            span_time = await page.query_selector_all('span.time')
            time = await span_time[0].inner_text()
            time_list.append(time)

            # 找到新页面中class为“weibo-text”的div元素并打印他们的text
            text_element = await page.query_selector_all('div.weibo-text')

            # 获取元素的 HTML
            element_html = await text_element[0].inner_html()

            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(element_html, 'html.parser')

            # 将所有的 <br> 标签替换为换行符
            for br in soup.find_all('br'):
                br.replace_with('\n')

            # 获取替换后的文本
            text = soup.get_text()
            content_text_list.append(text)

            print(time)
            print(text)
            print('\n')

            # 返回上一个界面
            await page.go_back()

            # 等待页面加载
            await asyncio.sleep(0.25)

        # 要写入的数据（存储为JSON格式）
        data = {
            'Text': content_text_list,
            'Time': time_list
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


        # 时间降序排列
        df.sort_values(by='Time', ascending=False, inplace=True)

        # 写入CSV文件
        df.to_csv(file_destination, index=False, encoding='utf-8')

        # 关闭浏览器
        await browser.close()
