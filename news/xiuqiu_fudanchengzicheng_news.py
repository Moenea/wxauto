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
        await page.goto('https://xueqiu.com/u/3697768583')

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
        # Get Content from each content div
        for item_main_div in item_main_divs:
            # datetime
            item_info_div = await item_main_div.query_selector('div.timeline__item__info')
            # Find the a element with the class 'date-and-source' that contains a span
            a_element = await item_info_div.query_selector('a.date-and-source')
            datetime = await a_element.inner_text()
            datetime = datetime.split('·')[0].replace('修改于','')
            print(datetime)

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
                print(text)
                print('')
                print('-----'*20)

        # 关闭浏览器
        await browser.close()

# 运行异步任务
asyncio.run(main())
