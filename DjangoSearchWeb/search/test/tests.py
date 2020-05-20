from django.test import TestCase

import re

import jieba
import numpy as np
from pandas import *
from sklearn.metrics import pairwise_distances
from bs4 import BeautifulSoup
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer

corpus = []
news = [[40146,"5月8日，国务院印发应对新型冠状病毒感染肺炎疫情联防联控机制关于做好新冠肺炎疫情常态化防控工作的指导意见。指导意见提出，按照相关技术指南，在落实防控措施前提下，全面开放商场、超市、宾馆、餐馆等生活场所；采取预约、限流等方式，开放公园、旅游景点、运动场所，图书馆、博物馆、美术馆等室内场馆，以及影剧院、游艺厅等密闭式娱乐休闲场所。","http://app.cctv.com/special/cportal/detail/arti/index.html?id=ArtizWqi5StmPHRzpDEHMqb8200508&isfromapp=1"],
        [40119,"根据世卫组织最新实时统计数据，目前全球确诊新冠肺炎病例3726292例，死亡257405例，中国以外超过364万例。","http://app.cctv.com/special/cportal/detail/arti/index.html?id=ArtiwiADdXQ9g9Yg6kdIUZZh200508&isfromapp=1"],
        [40103,"从5月8日零时起，香港放宽多项保持社交距离的防疫措施，包括餐馆每桌最多可坐4人的规定放宽至8人，限聚令同时也由4人放宽至8人等。而在6日，部分图书馆、博物馆以及室外运动场等也陆续开放。","http://app.cctv.com/special/cportal/detail/arti/index.html?id=ArtiJOfs5epOxe645uFXZgMl200508&isfromapp=1"]]
df = DataFrame(news, columns=['news_id', 'content', 'url'])
zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
for index, row in df.iterrows():
    print(index)
    content = row['content']
    bs = BeautifulSoup(content, "html.parser")
    segments = []
    segs = jieba.cut(bs.text)
    for seg in segs:
        if zhPattern.search(seg):
            segments.append(seg)
    corpus.append(' '.join(segments))

vectorizer = TfidfVectorizer()  # 该类会统计每个词语的tf-idf权值
tfidf = vectorizer.fit_transform(corpus)  # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
words = vectorizer.get_feature_names()
print(len(words))
print(words)
print(vectorizer.vocabulary_)
a = tfidf.todense()
print(a)

distance_matrix = pairwise_distances(
    tfidf,
    metric='cosine'
)

# for index, item in enumerate(distance_matrix):
#     # min_value = np.min(np.delete(item, index))
#     # min_index = np.argmin(np.delete(item, index))
#     b = np.argsort(item)
#     print("=" * 10 + "与%s相似的文章有:" % df.iloc[index, 0] + "=" * 10)
#     for index_2 in b:
#         print(df.iloc[index_2, 0], "余弦距离:%s" % item[index_2])

for index, item in enumerate(distance_matrix):
    if df.iloc[index, 0] == 40146:
        b = np.argsort(item)
        print("=" * 10 + "与%s相似的文章有:" % df.iloc[index, 0] + "(链接地址:%s)" % df.iloc[index, 2] + "=" * 10)
        for index_2 in b:
            print(df.iloc[index_2, 0], "余弦相似度:%s" % item[index_2], "链接地址:%s" % df.iloc[index_2, 2])