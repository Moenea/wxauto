from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, NavigableString
import asyncio

async def main():
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

        for div in divs:
            # 找到div中的所有直接子元素
            # children = [child for child in div.children if child.name == 'span']
            children = [child for child in div.children]
            
            # 检查直接子元素的数量
            if len(children) == 2 and children[0].name=='span' and children[1].name=='span':
                print(children[0].text)  # 打印第一个span的text
                
                # 找到第二个span中的所有div元素
                divs_in_span = children[1].find_all('div', recursive=False)
                
                # 检查div的数量
                if len(divs_in_span) == 1:
                    print(divs_in_span[0].text,'\n')
                elif len(divs_in_span) > 1:
                    for div_in_span in divs_in_span:
                        # 打印div元素本身的文本
                        for child in div_in_span.children:
                            if isinstance(child, NavigableString):
                                print(child,'\n')
                            elif child.name == 'strong':
                                print(child.string)

        # 关闭浏览器
        await browser.close()

# 运行异步任务
asyncio.run(main())
