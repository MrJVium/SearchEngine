import csv
from models.es_types import NewsType
from elasticsearch_dsl.connections import connections
es = connections.create_connection(hosts=["http://119.3.52.214:9200"], http_auth=("elastic:jin821950!"))

path = r"DXYNews.csv"
a = [0,2,3,4,5,6,7,8,14]

def gen_suggestion(index, info_tuple):
    # 根据字符串及权重，生成搜索建议
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            words = es.indices.analyze(body={'text': text, 'analyzer': "ik_max_word"})
            analyzed_words = set([r["token"] for r in words['tokens'] if len(r['token']) > 1])
            new_words = analyzed_words - used_words
            used_words = used_words | new_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), 'weight': weight})
    return suggests

if __name__ == "__main__":
    with open(path, 'r') as f:
        csv_read = csv.reader(f)
        for i, line in enumerate(csv_read):
            if i > 2:
                try:
                    news = NewsType()
                    news.pubDate = line[2]
                    news.title = line[3]
                    news.summary = line[4]
                    news.infoSource = line[5]
                    news.sourceUrl = line[6]
                    news.provinceId = line[7]
                    news.crawlTime = line[8]
                    news.provinceName = line[14]

                    news.meta.id = line[1]

                    news.suggest = gen_suggestion(NewsType.Index.name,
                                                   ((news.title, 10), (news.summary, 7)))
                    news.save()
                except:
                    pass



