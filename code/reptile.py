# -*- coding:utf-8 -*-
# By qixinlei
import urllib
import re, codecs
import time, random
import requests
from lxml import html
from urllib import parse
import csv
import pandas as pd

# 搜索关键字，这里只爬取了数据挖掘的数据，读者可以更换关键字爬取其他行业数据
key = '数据挖掘'

# 编码调整，如将“数据挖掘”编码成%25E6%2595%25B0%25E6%258D%25AE%25E6%258C%2596%25E6%258E%2598
key = parse.quote(parse.quote(key))

# 伪装爬取头部，以防止被网站禁止
headers = {'Host': 'search.51job.com',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)\
         Chrome/63.0.3239.132 Safari/537.36'}

# 打开Data_mining.csv文件，进行写入操作
csvFile = open("Data_mining.csv", 'w', newline='')
writer = csv.writer(csvFile)
writer.writerow(('link', 'job', 'company', 'salary', 'area', 'experience', \
                 'education', 'companytype', 'direction', 'describe'))


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

# 多页处理，下载到文件
def get_content(link):
    r1 = requests.get(link, headers, timeout=10)
    s = requests.session()
    s.keep_alive = False
    r1.encoding = 'gb2312'
    t1 = html.fromstring(r1.text)
    # print(link)
    job = t1.xpath('//div[@class="tHeader tHjob"]//h1/text()')[0].strip()
    # print(job)
    company = t1.xpath('//p[@class="cname"]/a/text()')[0].strip()
    # print(company)
    salary = t1.xpath('//div[@class="cn"]//strong/text()')[0].strip()
    # print(salary)
    area = t1.xpath('//p[@class="msg ltype"]/text()')[0].strip()
    print(get_area(area))
    # print(area)
    experience = t1.xpath('//p[@class="msg ltype"]/text()')[1].strip()
    # print(experience)
    education = t1.xpath('//p[@class="msg ltype"]/text()')[2].strip()
    # print(education)
    companytype = t1.xpath('//p[@class="at"]/text()')[0].strip()
    # print(companytype)
    companyscale = t1.xpath('//p[@class="at"]/text()')[1].strip()
    # print(companyscale)
    direction = t1.xpath('//div[@class="com_tag"]/p/a/text()')[0].strip()
    # print(direction)
    describe = t1.xpath('//div[@class="bmsg job_msg inbox"]//text()')
    # print(describe)
    writer.writerow((link, job, company, salary, area, experience, education, companytype, direction, describe))
    return True


# 主调动函数
# 爬取前三页信息
for i in range(1, 4):
    print('正在爬取第{}页信息'.format(i))
    links = get_links(i)
    area = {}
    for link in links:
        try:
            get_content(link)
        except:
            print("数据有缺失值")
            continue

# 关闭写入文件
csvFile.close()