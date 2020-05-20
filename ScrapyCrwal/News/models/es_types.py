from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text, Object, Integer
from elasticsearch_dsl.connections import connections

# connections.create_connection(hosts=["localhost"])
connections.create_connection(hosts=["http://119.3.52.214:9200"], http_auth=("elastic:jin821950!"))

class WeiboType(Document):
    suggest = Completion(analyzer='ik_max_word')
    id = Keyword()
    created_at = Date()
    user = Object()
    pics = Keyword(multi=True)
    reposts_count = Integer()
    comments_count = Integer()
    attitudes_count = Integer()
    text = Text(analyzer="ik_max_word")
    video_info = Object()

    class Index:
        name = "weibo"
        settings = {
            "number_of_shards": 4,
        }

class RumorType(Document):
    suggest = Completion(analyzer='ik_max_word')
    id = Keyword()
    title = Text(analyzer="ik_max_word")
    text = Text(analyzer="ik_max_word")
    abstract = Text(analyzer="ik_max_word")
    author = Keyword()
    authordesc = Keyword()
    date = Date()
    markstyle = Keyword()
    result = Keyword()
    explain = Keyword()
    tag = Text(analyzer="ik_max_word")
    coverimg = Keyword()

    class Index:
        name = "rumor"
        settings = {
            "number_of_shards": 1,
        }

class NewsType(Document):
    suggest = Completion(analyzer='ik_max_word')
    id = Keyword()
    pubDate = Date()
    title = Text(analyzer="ik_max_word")
    summary = Text(analyzer="ik_max_word")
    infoSource = Keyword()
    sourceUrl = Keyword()
    provinceId = Keyword()
    crawlTime = Date()
    provinceName = Text(analyzer="ik_max_word")

    class Index:
        name = "news"
        settings = {
            "number_of_shards": 1,
        }




if __name__ == "__main__":
    # RumorType.init()
    # WeiboType.init()
    NewsType.init()
    # re_datas = []
    # s = RumorType.search()
    # s = s.suggest('My_SUGGESTION', "30", completion={
    #     'field': 'suggest', 'fuzzy': {
    #         'fuzziness': 2
    #     },
    #     'size': 10
    # })
    # suggestions = s.execute()
    # for match in suggestions.suggest.My_SUGGESTION[0].options:
    #     source = match._source
    #     re_datas.append(source['title'])
    # print(re_datas)
