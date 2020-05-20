import os
import os.path
import re
import json
import requests
from bs4 import BeautifulSoup
from django.test import TestCase
from datetime import datetime
# Create your tests here.
# m = ['January', 'February', 'April']
# fileDir = './data/'+m[1]+'/'
# predictDir = fileDir + 'predict/'
# wordDir = fileDir + 'word/'
# allType = fileDir + 'typeCount'
# allWord = fileDir + 'wordCount'
#
# pfn = os.listdir(predictDir)
# pfn.sort()
# print(pfn)



# st = datetime.now()
#
# # wordcount
# wc = []
# tc = []
# with open(allWord, 'r') as f:
#     while True:
#         s = f.readline()
#         if s:
#             t = s.split(' ')
#             wc.append({'name': t[0], 'value': int(t[1])})
#         else:
#             break
#
# with open(predictDir+'2020-02-01', 'r') as f:
#     while True:
#         s = f.readline()
#         if s:
#             t = s.split(' ')
#             tc.append({'name': t[0], 'value': int(t[1])})
#         else:
#             break
# et = datetime.now()
# print((et-st).total_seconds())
# print(tc)

session = requests.session()
r = session.get(url='https://ncov.dxy.cn/ncovh5/view/pneumonia')
soup = BeautifulSoup(r.content, 'lxml')

news_chinese = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getTimelineService1'})))
# if news_chinese:
#     self.news_parser(news=news_chinese)
n = news_chinese.group(0)
print(n)
k = json.loads(n)
overall_information = re.search(r'(\{"id".*\})\}',
                                str(soup.find('script', attrs={'id': 'getStatisticsService'})))
o = overall_information.group(0)
# if overall_information:
#     self.overall_parser(overall_information=overall_information)
a = 1