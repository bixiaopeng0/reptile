'''
2019/11/25
省份 平均工资 最小工资 最多工资 中文数
'''


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

# 利用正则表达式提取月薪，把待遇规范成千/月的形式
def get_salary(salary):
    if '-' in salary:  # 针对1-2万/月或者10-20万/年的情况，包含-
        low_salary = re.findall(re.compile('(\d*\.?\d+)'), salary)[0]
        high_salary = re.findall(re.compile('(\d?\.?\d+)'), salary)[1]
        if u'万' in salary and u'年' in salary:  # 单位统一成千/月的形式
            low_salary = float(low_salary) / 12 * 10
            high_salary = float(high_salary) / 12 * 10
        elif u'万' in salary and u'月' in salary:
            low_salary = float(low_salary) * 10
            high_salary = float(high_salary) * 10
    else:  # 针对20万以上/年和100元/天这种情况，不包含-，取最低工资，没有最高工资
        high_salary = ""
        if u'面议' in salary:
            low_salary = ""
        else:
            low_salary = re.findall(re.compile('(\d*\.?\d+)'), salary)[0]
        if u'万' in salary and u'年' in salary:  # 单位统一成千/月的形式
            low_salary = float(low_salary) / 12 * 10
        elif u'万' in salary and u'月' in salary:
            low_salary = float(low_salary) * 10
        elif u'元' in salary and u'天' in salary:
            low_salary = float(low_salary) / 1000 * 21  # 每月工作日21天

    return low_salary, high_salary


def get_content_salary(link):
    r1 = requests.get(link, headers, timeout=10)
    s = requests.session()
    s.keep_alive = False
    r1.encoding = 'gb2312'
    t1 = html.fromstring(r1.text)
    salary = t1.xpath('//div[@class="cn"]//strong/text()')[0].strip()
    return get_salary(salary)



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
    csvFile = open("area_salary.csv", 'w', newline='')
    writer = csv.writer(csvFile)
    writer.writerow(('地区','工资'))

    for i in range(len(percent)):
        #工资
        writer.writerow((label[i],percent[i]))
        #百分比
        # writer.writerow((label[i],percent[i]/sum(percent)))

    csvFile.close()




# 主调动函数
# 爬取前三页信息

#取工资的平均值--浮点数
#出现的次数必须大于N
#清洗数据删除范围过大的数据
def run(N):
    salary_dict = {}
    area_nums_dict = {}
    for i in range(1, 10):
        print('正在爬取第{}页信息'.format(i))
        links = get_links(i)

        for link in links:
            try:
                area = get_content_area(link)
                salary=get_content_salary(link)
                print(area,salary)
                money_area = float(salary[1])-float(salary[0] )
                if money_area>9:
                    print(money_area)
                    continue
                average_salary = (float(salary[0])+float(salary[1]))/2
                print(average_salary)
                if area not in salary_dict:
                    salary_dict[area]= average_salary
                    area_nums_dict[area] = 1
                else:
                    salary_dict[area] = (average_salary +salary_dict[area])/2
                    area_nums_dict[area]+=1
                print("salary",salary_dict)

            except:
                print("数据有缺失值")
                continue

    for key,value in area_nums_dict.items():
        if value < N :
            salary_dict.pop(key)
    print(salary_dict)

    list1 = sorted(salary_dict.items(), key=lambda x: x[1], reverse=True)
    label = []
    label_data = []
    for key,value in list1:
        label.append(key)
        label_data.append(value)

    print(label)
    print(label_data)
    plot_data(label_data,label)
    write_csv(label_data,label)

    # list1 = sorted(area_dict.items(), key=lambda x: x[1],reverse=True)
    # print(list1)
    # label = []
    # label_data = []
    # for key,value in list1:
    #     if value >4:
    #         label.append(key)
    #         label_data.append(value)
    #
    #
    # print(label)
    # print(label_data)
    # plot_data(label_data,label)
    # write_csv(label_data,label)

if __name__ == '__main__':
    run(5)



