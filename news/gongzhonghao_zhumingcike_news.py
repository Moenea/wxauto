from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    # page.goto("https://mp.weixin.qq.com/s/teKlF_mbVhkha-wTBBwM1g")
    page.goto("https://mp.weixin.qq.com/s/GvoX7MeP0mr1JqFwaQAfEQ")

    
    # 获取并打印 id 为 "publish_time" 的 em 元素的内容
    publish_time = page.eval_on_selector("#publish_time", "e => e.innerText")
    print(publish_time)
    
    # 获取并打印 id 为 "js_content" 的 div 元素的内容
    div_content = page.eval_on_selector("#js_content", "e => e.innerText")
    print(div_content)
    
    browser.close()


#!/usr/bin/env -S poetry run python

from openai import OpenAI
import os

key = os.getenv('OPENAI_API_KEY')
url = os.getenv('OPENAI_BASE_URL')

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(api_key=key, base_url=url)

# Non-streaming:
print("----- standard request -----",end='\n\n')
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": '仔细看一看这些内容，分析一下目前市场情绪，并对接下来市场反应做预判：'+div_content,
        },
    ],
)
print(completion.choices[0].message.content)