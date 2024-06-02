import aiohttp
import os
import asyncio
from datetime import datetime

_temp_file_path = './news_pic/self-attention-matrix-calculation-queries.png'
_temp_directory = './news_pic'

if (os.path.commonpath([_temp_file_path, _temp_directory]) == _temp_directory):
    print(1)
else:
    print(0)


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

# # 示例用法
# _temp_file_path = './news_data/weibo_xianglong18duan.csv'
# _temp_directory = './news_data/'

if is_in_directory(_temp_file_path, _temp_directory):
    print(f"{_temp_file_path} 位于 {_temp_directory} 目录中")
else:
    print(f"{_temp_file_path} 不在 {_temp_directory} 目录中")
