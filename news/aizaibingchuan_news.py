from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup


async def main():
    async with async_playwright() as p:
        # 创建一个浏览器实例
        browser = await p.chromium.launch()

        # 创建一个新的页面
        page = await browser.new_page()

        # 打开页面
        await page.goto('https://m.weibo.cn/u/3819648373')

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

            # 找到新页面中class为“weibo-text”的div元素并打印他们的text
            text_element = await page.query_selector_all('div.weibo-text')

            # 获取元素的 HTML
            element_html = await text_element[0].inner_html()

            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(element_html, 'html.parser')
            text = soup.get_text()

            # 将所有的 <br> 标签替换为换行符
            for br in soup.find_all('br'):
                br.replace_with('\n')

            print(time)
            print(text)
            print('')
            print('---------------'*5)
            print('')

            # 返回上一个界面
            await page.go_back()

            # 等待页面加载
            await asyncio.sleep(0.25)

        # 关闭浏览器
        await browser.close()

# 运行异步任务
asyncio.run(main())
