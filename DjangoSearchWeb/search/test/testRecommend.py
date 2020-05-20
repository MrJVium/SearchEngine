import re

import jieba

from pandas import *
from sklearn.metrics import pairwise_distances
from bs4 import BeautifulSoup
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer
from mysql_util import MySqlUtils


class ContentRecommend(object):

    def __init__(self):
        DATABASE_CONFIG = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "passwd": "root",
            "db": "recommend",
            "charset": "utf8",
        }

        self.con = MySqlUtils(DATABASE_CONFIG)

        self.recommend_count = 10
        self.all_count = 1000
        self.reload_data()

    def reload_data(self):
        corpus = []
        sql = "select a.news_id,a.content,b.source_url as url from news_content as a left join news as b on a.news_id=b.news_id"
        self.df = DataFrame(list(self.con.query(sql)), columns=['news_id', 'content', 'url'])
        zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
        for index, row in self.df[0:self.all_count].iterrows():
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

        self.distance_matrix = pairwise_distances(
            tfidf,
            metric='cosine'
        )

    def analysis(self):
        for index, item in enumerate(self.distance_matrix):
            #min_value = np.min(np.delete(item, index))
            #min_index = np.argmin(np.delete(item, index))
            b = np.argsort(item)[1:self.recommend_count]
            print("="*10 + "与%s相似的文章有:" % self.df.iloc[index, 0] + "="*10 )
            for index_2 in b:
                print(self.df.iloc[index_2, 0], "余弦距离:%s" % item[index_2])

    def get_similar_news_id(self, news_id):
        for index, item in enumerate(self.distance_matrix):
            if self.df.iloc[index, 0] == news_id:
                b = np.argsort(item)[1:self.recommend_count]
                print("="*10 + "与%s相似的文章有:" % self.df.iloc[index, 0] + "(链接地址:%s)" % self.df.iloc[index, 2] + "="*10 )
                for index_2 in b:
                    print(self.df.iloc[index_2, 0], "余弦相似度:%s" % item[index_2], "链接地址:%s" % self.df.iloc[index_2, 2])

    def get_recommend_news_by_uid(self, uid):
        pass

    def input_news_id(self):
        while 1:
            print("输入newsId:")
            news_id = input()
            self.get_similar_news_id(news_id)


if __name__ == '__main__':
    ContentRecommend().input_news_id()