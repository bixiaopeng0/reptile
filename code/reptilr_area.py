# -*- coding:utf-8 -*-
import re
import requests
from lxml import html
from urllib import parse
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import csv

# 搜索关键字，这里只爬取了数据挖掘的数据，读者可以更换关键字爬取其他行业数据
key = '程序员'

# 编码调整，如将“数据挖掘”编码成%25E6%2595%25B0%25E6%258D%25AE%25E6%258C%2596%25E6%258E%2598
key = parse.quote(parse.quote(key))

# 伪装爬取头部，以防止被网站禁止
headers = {'Host': 'search.51job.com',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)\
         Chrome/63.0.3239.132 Safari/537.36'}


# 获取职位详细页面
def get_links(page):
    url = 'http://search.51job.com/list/000000,000000,0000,00,9,99,' + key + ',2,' + str(page) + '.html'
    print(url)
    r = requests.get(url, headers, timeout=1)
    s = requests.session()
    s.keep_alive = False
    r.encoding = 'gbk'
    reg = re.compile(r'class="t1 ">.*? <a target="_blank" title=".*?" href="(.*?)".*? <span class="t2">', re.S)
    links = re.findall(reg, r.text)
    return links


def get_area(area):
    b = pd.Series(area)
    c = b.str.split('-')
    return c[0][0]

def get_content_area(link):
    r1 = requests.get(link, headers, timeout=10)
    s = requests.session()
    s.keep_alive = False
    r1.encoding = 'gb2312'
    t1 = html.fromstring(r1.text)
    area = t1.xpath('//p[@class="msg ltype"]/text()')[0].strip()
    return get_area(area)



def plot_data(percent,label):
    plt.style.use('ggplot')
    # plt.rcParams['font.sans-serif'] = ['FangSong']
    plt.rcParams['axes.unicode_minus'] = False
    plt.axes(aspect='equal')

    from matplotlib.font_manager import FontProperties

    font = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc', size=16)
    p = plt.pie(x=percent, labels=label,autopct='%1.1f%%')
    for front in p[1]:
        front.set_fontproperties(matplotlib.font_manager.FontProperties(
            fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc'))

    plt.xticks(())
    plt.yticks(())
    # 添加图标题
    plt.title(u'程序员招聘地区分布',fontproperties=font)
    plt.show()



def write_csv(percent,label):
    # 打开Data_mining.csv文件，进行写入操作
    csvFile = open("area.csv", 'w', newline='')
    writer = csv.writer(csvFile)
    writer.writerow(('地区','占比'))

    for i in range(len(percent)):
        writer.writerow((label[i],percent[i]/sum(percent)))

    csvFile.close()




# 主调动函数
# 爬取前三页信息

def run():
    area_dict = {}
    for i in range(1, 10):
        print('正在爬取第{}页信息'.format(i))
        links = get_links(i)

        for link in links:
            try:
                area=get_content_area(link)
                if area in area_dict:
                    area_dict[area] +=1
                else:
                    area_dict[area] = 1
            except:
                print("数据有缺失值")
                continue
    list1 = sorted(area_dict.items(), key=lambda x: x[1],reverse=True)
    print(list1)
    label = []
    label_data = []
    for key,value in list1:
        if value >4:
            label.append(key)
            label_data.append(value)


    print(label)
    print(label_data)
    plot_data(label_data,label)
    write_csv(label_data,label)

if __name__ == '__main__':
    run()

