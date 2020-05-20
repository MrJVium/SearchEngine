import json
import os
from bs4 import BeautifulSoup
import requests
import time
import re
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime

# Create your views here.
from django.views.generic.base import View

months = {1: 'January', 2: 'February', 4: 'April'}

# st = datetime.now()

class PredictCountViews(View):
    def get(self, request):
        m = request.GET.get('month', 1)
        m = int(m)
        fileDir = './data/' + months[m] + '/'
        predictDir = fileDir + 'predict/'
        wordDir = fileDir + 'word/'
        allType = fileDir + 'typeCount'
        allWord = fileDir + 'wordCount'
        typeCnt = []
        allCnt = {}
        pfn = os.listdir(predictDir)
        pfn.sort()
        with open(allType, 'r') as f:
            while True:
                s = f.readline()
                if s:
                    t = s.split(' ')
                    allCnt[t[0]] = int(t[1])
                else:
                    break
        for i in pfn:
            tmp = {'date': i}
            tmpCnt = {'乐观': 0, '平静': 0, '悲伤': 0, '愤怒': 0, '担忧': 0}
            with open(predictDir + i, 'r') as f:
                while True:
                    s = f.readline()
                    if s:
                        t = s.split(' ')
                        tmpCnt[t[0]] = int(t[1])
                    else:
                        break
            tmp['value'] = tmpCnt
            typeCnt.append(tmp)
        return JsonResponse({'allCount': allCnt, "typeCount": typeCnt}, safe=False)

class WordCountViews(View):
    def get(self, request):
        m = request.GET.get('month', 1)
        m = int(m)
        date = request.GET.get('date', '')
        fileDir = './data/' + months[m] + '/'
        predictDir = fileDir + 'predict/'
        wordDir = fileDir + 'word/'
        allType = fileDir + 'typeCount'
        allWord = fileDir + 'wordCount'
        wc = []
        if date:
            with open(wordDir+date, 'r') as f:
                while True:
                    s = f.readline()
                    if s:
                        t = s.split(' ')
                        if (t[0]=='展开' or t[0]=='全文') or int(t[1]) < 50:
                            continue
                        wc.append({'name': t[0], 'value': int(t[1])})
                    else:
                        break
        else:
            with open(allWord, 'r') as f:
                while True:
                    s = f.readline()
                    if s:
                        t = s.split(' ')
                        if int(t[1]) < 50:
                            continue
                        wc.append({'name': t[0], 'value': int(t[1])})
                    else:
                        break

        return JsonResponse(wc, safe=False)

session = requests.session()
class RealTimeDataView(View):
    def get(self, requests):

        r = session.get(url='https://ncov.dxy.cn/ncovh5/view/pneumonia')
        soup = BeautifulSoup(r.content, 'html.parser')

        news_chinese = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getTimelineService1'}))).group(0)


        overall_information = re.search(r'(\{"id".*\})\}',
                                        str(soup.find('script', attrs={'id': 'getStatisticsService'}))).group(1)
        tech_names = {'currentConfirmedCount', 'confirmedCount', 'suspectedCount', 'curedCount', 'deadCount', 'seriousCount', 'suspectedIncr', 'currentConfirmedIncr', 'confirmedIncr', 'curedIncr', 'deadIncr', 'seriousIncr'}
        return JsonResponse({'data': {key: value for key, value in json.loads(overall_information).items() if key in tech_names}, 'news': json.loads(news_chinese)})