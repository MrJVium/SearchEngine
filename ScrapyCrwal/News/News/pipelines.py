# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.exceptions import DropItem
from scrapy.exporters import JsonItemExporter

from News.items import WeiboNewsItem, WeiboCommentsItem, RumorsItem
from models.es_types import RumorType


class NewsPipeline(object):
    def process_item(self, item, spider):
        return item

class RedisTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        import redis
        dbparms = dict(
            host=settings["REDIS_HOST"],
            db=settings["REDIS_DBNAME"],
            port=settings["REDIS_PORT"],
            password=settings["REDIS_PASSWORD"],
        )
        pool = redis.ConnectionPool(**dbparms)
        dbpool = redis.StrictRedis(connection_pool=pool)
        # 别忘了要传过去实例化
        return cls(dbpool)

    def process_item(self, item, spider):
        if isinstance(item, WeiboCommentsItem):
            if self.dbpool.sadd("Comments", item["id"]) == 1:
                return item
            else:
                raise DropItem("Duplicate Comments item found: %s" % item)
        elif isinstance(item, WeiboNewsItem):
            if self.dbpool.sadd("News", item["id"]) == 1:
                return item
            else:
                raise DropItem("Duplicate News item found: %s" % item)
        elif isinstance(item, RumorsItem):
            if self.dbpool.sadd("Rumors", item["id"]) == 1:
                return item
            else:
                raise DropItem("Duplicate Rumors item found: %s" % item)
        else:
            return item


class NewsJsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open(r"News.json", "a", encoding="utf-8")

    def process_item(self, item, spider):
        if isinstance(item, WeiboNewsItem):
            lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
            self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class CommentsJsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open(r"Comments.json", "a", encoding="utf-8")

    def process_item(self, item, spider):
        if isinstance(item, WeiboCommentsItem):
            lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
            self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class RumorsJsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open(r"Rumors.json", "a", encoding="utf-8")

    def process_item(self, item, spider):
        if isinstance(item, RumorsItem):
            lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
            self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()

class ElasticsearchPipeline(object):

    def process_item(self, item, spider):
        item.save2es()
        return item