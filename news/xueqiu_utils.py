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


    elif "分钟前" in time_str:
        number = int(time_str.split("分钟前")[0])
        time_obj = now-timedelta(minutes=number)

        time_obj = datetime.strftime(time_obj, "%Y-%m-%d %H:%M:S")
        return datetime.strptime(time_obj, "%Y-%m-%d %H:%M:S")

    elif "小时前" in time_str:
        number = int(time_str.split("小时前")[0])
        time_obj = now-timedelta(hours=number)

        time_obj = datetime.strftime(time_obj, "%Y-%m-%d %H:%M:S")
        return datetime.strptime(time_obj, "%Y-%m-%d %H:%M:S")

    try:
        # 尝试按照指定格式解析时间字符串
        datetime_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        pass
    
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

        # 通过JavaScript查找文本内容为“跳过”的<a>元素并点击
        await page.evaluate('''() => {
            const elements = Array.from(document.querySelectorAll('a'));
            const targetElement = elements.find(element => element.textContent.trim() === '跳过');
            if(targetElement) targetElement.click();
        }''')

        # Wait for the page to react to the click
        await asyncio.sleep(0.25)

        # Click the <a> element with class name "close close_jianlian"
        close_element = await page.query_selector('a.close.close_jianlian')
        if close_element:
            await close_element.click()

        # Expand all divs
        expand_buttons = await page.query_selector_all('a.timeline__expand__control')
        # Click each expand button
        for expand_button in expand_buttons:
            await expand_button.click()
            await asyncio.sleep(0.25)  # wait for each expand action to complete

        # For each Items
        item_main_divs = await page.query_selector_all('div.timeline__item__main')
        time_list = []
        content_text_list = []
        # Get Content from each content div
        for item_main_div in item_main_divs:
            # datetime
            item_info_div = await item_main_div.query_selector('div.timeline__item__info')
            # Find the a element with the class 'date-and-source' that contains a span
            a_element = await item_info_div.query_selector('a.date-and-source')
            datetime = await a_element.inner_text()
            datetime = datetime.split('·')[0].replace('修改于','')

            # text content
            item_div = await item_main_div.query_selector('div.timeline__item__content')
            contentElement = await item_div.query_selector('.content.content--detail')
            if not contentElement:
                contentElement = await item_div.query_selector('.content.content--description')
            if contentElement:
                # text = await contentElement.text_content()
                text = await contentElement.inner_text()
                link_elements = await contentElement.query_selector_all('a')
                for link in link_elements:
                    link_text = await link.inner_text()
                    text = text.replace(link_text, '')

                time_list.append(datetime)
                content_text_list.append(text)

                # print(datetime)
                # print()
                # print(text)
                # print('\n')

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
            df_stored['Time'] = pd.to_datetime(df_stored['Time'], format='%Y-%m-%d %H:%M:%S')
        except:
            time_series = []

        # 进行drop操作
        drop_index = []
        for i,e in enumerate(df['Time']):
            if str(e) in time_series:
                drop_index.append(i)
            if str(df.iloc[i,0]) == '' or str(df.iloc[i,0]) == '\n':
                drop_index.append(i)
        df.drop(drop_index, inplace=True)

        # 新数据与原数据合并
        if len(time_series) != 0:
            df = pd.concat([df, df_stored], axis=0, ignore_index=True)

        # 再次检查Text列是否有重复，有则删去，保留原始的哪一个row（那是“分钟前”计算的，更加准确）
        df.drop_duplicates(subset='Text', keep='last', inplace=True)

        # 时间降序排列
        df.sort_values(by='Time', ascending=False, inplace=True)

        # 写入CSV文件
        df.to_csv(file_destination, index=False, encoding='utf-8')

        # 关闭浏览器
        await browser.close()
