import subprocess
import os
import pandas as pd
import json

def update_news(news_name, resouce_name):
    # 指定文件路径
    csv_file_path = f'./news_data/{news_name}.csv'
    py_file_path = f'./news/{news_name}_news.py'

    # 判断消息来源，比如'./news/cls_news.py'就是 【cls】
    resouce = '【' + resouce_name + '】'

    # 判断文件是否存在，若存在直接看rows；若不存在先初始化csv然后看rows
    if os.path.exists(csv_file_path):
        text_df = pd.read_csv(csv_file_path, encoding='utf-8')
        item_num_before = text_df.shape[0]
    else:
        print('Initializing...')
        subprocess.run(['python', py_file_path])
        text_df = pd.read_csv(csv_file_path, encoding='utf-8')
        item_num_before = text_df.shape[0]

    subprocess.run(['python', py_file_path])
    text_df = pd.read_csv(csv_file_path, encoding='utf-8')
    item_num_after = text_df.shape[0]

    if 'cls' in csv_file_path:
        # cls 需要将 JSON 字符串转换回列表
        text_df['Text'] = text_df['Text'].apply(json.loads)

        text_list = []
        if item_num_before != item_num_after:
            for i in range(item_num_after-item_num_before-1,-1,-1):
                time = text_df.iloc[i,1]
                data_list = text_df.iloc[i,0]
                text = resouce + '\n' + time + "\n\n" + "\n\n".join(data_list)
                # print(text)
                text_list.append(text)

    else:
        text_df['Time'] = pd.to_datetime(text_df['Time'], format='%Y-%m-%d %H:%M:%S')
        text_list = []
        pic_list = []
        if item_num_before != item_num_after:
            for i in range(item_num_after-item_num_before-1,-1,-1):
                text = resouce + '\n' + str(text_df.iloc[i,1])+"\n\n"+text_df.iloc[i,0]
                # print(text)
                text_list.append(text)

                # 读取照片路径
                pic_list.append(text_df.iloc[i,2])

    return text_list, pic_list

if __name__ == '__main__':
    # news_name = 'cls_jiahong'
    # news_name = 'weibo_tangshuzhuren'
    news_name = 'xueqiu_fudanchengzicheng'
    text_list, pic_list = update_news(news_name, 'TESTING PHASE')
    for i,e in enumerate(text_list):
        print(e)
        print(pic_list[i])
        print('\n\n')