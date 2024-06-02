import aiohttp
import os
import asyncio
from datetime import datetime

async def download_image(url):
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
            if response.status != 200:
                print(f"Failed to download image. Status code: {response.status}")
                return 'No_Pic'
            
            pic_id = datetime.now().strftime("%Y%m%d%H%M%S")
            file_path = './news_pic/' + url.split('/')[-1] + '-' + pic_id + '_image.jpg'
            
            # 将图片写入临时文件
            temp_file_path = file_path + '.tmp'
            with open(temp_file_path, 'wb') as file:
                file.write(await response.read())
            
            # 检查文件大小
            file_size = os.path.getsize(temp_file_path)
            if file_size < 5 * 1024:  # 5KB = 5 * 1024 bytes
                os.remove(temp_file_path)
                print(f"Image size is less than 5KB, not saving the file: {temp_file_path}")
                return 'No_Pic'
            else:
                os.rename(temp_file_path, file_path)
                print(f"Image successfully downloaded: {file_path}")
                return file_path

# 主函数
async def main():
    url = 'https://wx4.sinaimg.cn/large/7811cf6bly1hq6dmmskqaj20ui0s77pu.jpg' # class="pswp__img"
    await download_image(url)

# 运行主函数
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
