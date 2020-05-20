from django.db import models
from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text, Object, Integer
from elasticsearch_dsl.connections import connections

# connections.create_connection(hosts=["localhost"])
es = connections.create_connection(hosts=["http://119.3.52.214:9200"], http_auth=("elastic:jin821950!"))

# Create your models here.


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
            "number_of_shards": 4,
        }

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

class EsArea(Document):
    suggest = Completion(analyzer='ik_max_word')
    continentName = Text(analyzer='ik_max_word')
    countryName = Text(analyzer='ik_max_word')
    provinceName = Text(analyzer='ik_max_word')
    cityName = Text(analyzer='ik_max_word')
    confirmedCount = Integer()
    suspectedCount = Integer()
    curedCount = Integer()
    deadCount = Integer()
    currentConfirmedCount = Integer()
    updateTime = Date()

    class Index:
        name = "area"
        settings = {
            "number_of_shards": 3,
        }

class EsOverAll(Document):
    confirmedCount = Integer()
    confirmedIncr = Integer()
    suspectedCount = Integer()
    suspectedIncr = Integer()
    curedCount = Integer()
    curedIncr = Integer()
    deadCount = Integer()
    deadIncr = Integer()
    currentConfirmedCount = Integer()
    currentConfirmedIncr = Integer()
    updateTime = Date()

    class Index:
        name = "overall"
        settings = {
            "number_of_shards": 3,
        }

class JsonModel():
    @classmethod
    def success(cls, data):
        return(dict({
                        "code": 1,
                        "msg": "success"
                    }, **data))
    @classmethod
    def failed(cls, data):
        return(dict({
                        "code": 0,
                        "msg": "failed"
                    }, **data))