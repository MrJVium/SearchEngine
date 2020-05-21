# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import time
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Identity, Join

from models.es_types import RumorType, WeiboType
from elasticsearch_dsl.connections import connections

# es = connections.create_connection(hosts=["localhost"])
es = connections.create_connection(hosts=[""], http_auth=(""))
class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewsItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

def get_date(value):
    if value:
        move_timezone = time.strptime(value.replace("+0800 ", ""))
        return time.strftime("%Y-%m-%d %H:%M:%S", move_timezone)
    else:
        return "1970-07-01"

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

class WeiboNewsItem(scrapy.Item):
    id = scrapy.Field()
    created_at = scrapy.Field(
        input_processor=MapCompose(get_date)
    )
    user = scrapy.Field()
    pics = scrapy.Field(
        output_processor=Identity()
    )
    reposts_count = scrapy.Field()
    comments_count = scrapy.Field()
    attitudes_count = scrapy.Field()
    text = scrapy.Field()
    video_info = scrapy.Field()
    
    def save2es(self):
        weibo = WeiboType()
        weibo.text = self.get("text", "")
        weibo.created_at = self['created_at']
        weibo.user = self['user']
        weibo.pics = self.get('pics', [])
        weibo.reposts_count = self['reposts_count']
        weibo.comments_count = self['comments_count']
        weibo.attitudes_count = self['attitudes_count']
        weibo.video_info = self.get('video_info', {})

        weibo.meta.id = self['id']

        weibo.suggest = gen_suggestion(WeiboType.Index.name, ((weibo.text, 10),))

        weibo.save()
        return
    
class WeiboCommentsItem(scrapy.Item):
    id = scrapy.Field()
    text = scrapy.Field()
    like_count = scrapy.Field()
    created_at = scrapy.Field(
        input_processor=MapCompose(get_date)
    )

    def save2es(self):
        return

class RumorsItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field(
        output_processor=Join(separator=",")
    )
    abstract = scrapy.Field(
        output_processor=Join(separator=",")
    )
    author = scrapy.Field()
    authordesc = scrapy.Field()
    date = scrapy.Field()
    markstyle = scrapy.Field()
    result = scrapy.Field()
    explain = scrapy.Field()
    tag = scrapy.Field(
        output_processor=Join(separator=",")
    )
    coverimg = scrapy.Field()

    def save2es(self):
        rumor = RumorType()
        rumor.text = self.get("text", "")
        rumor.title = self['title']
        rumor.abstract = self['abstract']
        rumor.coverimg = self['coverimg']
        rumor.author = self['author']
        rumor.authordesc = self['authordesc']
        rumor.date = self['date']
        rumor.explain = self['explain']
        rumor.markstyle = self['markstyle']
        rumor.result = self['result']
        rumor.tag = self['tag']
        rumor.meta.id = self['id']

        rumor.suggest = gen_suggestion(RumorType.Index.name, ((rumor.title, 10), (rumor.abstract, 7), (rumor.text, 7)))

        rumor.save()
        return
