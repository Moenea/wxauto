import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
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


async def download_image(url, file_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://weibo.com/',  # 添加 Referer 头
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:

            # 获取文件路径和目录的绝对路径
            _temp_file_path = file_path
            _temp_directory = file_path.split('/')[0]+'/'+file_path.split('/')[1]
            
            # True的时候说明此图片已下载过，无需重复下载
            if is_in_directory(_temp_file_path, _temp_directory): 
                pass
            else:
                if response.status != 200:
                    print(f"Failed to download image. Status code: {response.status}")
                
                # 将图片写入临时文件
                with open(file_path, 'wb') as file:
                    file.write(await response.read())
            
                print(f"Image successfully downloaded: {file_path}")
                # # 检查文件大小
                # file_size = os.path.getsize(file_path)
                # if file_size < 10 * 1024:  # 10KB = 10 * 1024 bytes 避免下载表情作为图片
                #     os.remove(file_path)
                #     print(f"Image size is less than 10KB, not saving the file: {file_path}")
                # else:
                #     print(f"Image successfully downloaded: {file_path}")


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
        pic_list = []
        for index, element in enumerate(elements):
            # 获取元素的文本
            element_text = await element.text_content()

            # 选择包含特定文本的 div.weibo-text 元素
            selector = f'div.weibo-text:has-text("{element_text}")'
            
            # 获取该元素的边界框信息
            element = await page.query_selector(selector)
            bounding_box = await element.bounding_box()
            
            # 计算左侧位置，一般链接不会放置在左侧
            left_center_position = {'x': bounding_box['height'] / 5, 'y': bounding_box['height'] / 5}

            # 点击左侧位置
            await page.click(selector, position=left_center_position)

            # 等待新页面加载
            await asyncio.sleep(0.25)

            # 获取该条post的时间
            span_time = await page.query_selector_all('span.time')
            time = await span_time[0].inner_text()
            time_list.append(time)

            # 找weibo-og元素，里面含有text和图片
            div_weibo_og = await page.query_selector('div.weibo-og')

            # 找到新页面中class为“weibo-text”的div元素并打印他们的text
            text_element = await div_weibo_og.query_selector('div.weibo-text')

            # 获取元素的 HTML
            element_html = await text_element.inner_html()

            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(element_html, 'html.parser')

            # 将所有的 <br> 标签替换为换行符
            for br in soup.find_all('br'):
                br.replace_with('\n')

            # 获取替换后的文本
            text = soup.get_text()
            if "...全文" in text: # 在已经存储过本文本的时候，有时候会有莫名bug，点不开全文，并且文本中包含【...全文】的字样
                continue
            content_text_list.append(text)
            
            try:
                # 尝试寻找 div_weibo_og 中的 img 元素
                img_elements = await div_weibo_og.query_selector('img')
                img_src = await img_elements.get_attribute('src')
                large_img_src = img_src.replace('orj360','large')

                pic_id = convert_time(time).strftime("%Y%m%d%H%M%S")
                file_path = './news_pic/' + file_destination.split('/')[-1].split('.')[0] + '_' + pic_id + '_image.jpg'
                await download_image(large_img_src, file_path)
            except:
                file_path = 'No_Pic'

            pic_list.append(file_path)

            # print(time)
            # print(text)
            # print('\n')

            # 返回上一个界面
            await page.go_back()

            # 等待页面加载
            await asyncio.sleep(0.25)

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
