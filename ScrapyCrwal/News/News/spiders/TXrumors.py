# -*- coding: utf-8 -*-
import random
from urllib import parse
import re
import json
import gc
# import redis

import scrapy
from scrapy import Request

from News.items import NewsItemLoader, RumorsItem


class TxrumorsSpider(scrapy.Spider):
    name = 'TXrumors'
    allowed_domains = ['vp.fact.qq.com']
    start_urls = ['https://vp.fact.qq.com/loadmore?page=0']

    def parse(self, response):
        contents = json.loads(response.body.decode("utf-8")).get("content", [])
        page = response.meta.get("page", 0)
        pageurl = "https://vp.fact.qq.com/loadmore?page="
        articleurl = "https://vp.fact.qq.com/article?id="
        for i, rumor in enumerate(contents):
            yield Request(url=articleurl+rumor["id"], meta={"rumor":rumor}, callback=self.parse_detail)
        if page < 56:
            yield Request(url=pageurl+str(page), meta={"page": page+1},callback=self.parse)

    def parse_detail(self, response):
        item_loader = NewsItemLoader(item=RumorsItem(), response=response)
        rumor = response.meta.get("rumor", {})
        item_loader.add_value("id", rumor["id"])
        item_loader.add_value("title", rumor["title"])
        item_loader.add_css("text", "div.question.text > p::text")
        item_loader.add_css("abstract", "div.check_content_points ul > li::text")
        # 把 text 做一下合并
        item_loader.add_value("author", rumor["author"])
        item_loader.add_value("authordesc", rumor["authordesc"])
        item_loader.add_value("date", rumor["date"])
        item_loader.add_value("markstyle", rumor["markstyle"])
        item_loader.add_value("result", rumor["result"])
        item_loader.add_value("explain", rumor["explain"])
        item_loader.add_value("tag", rumor["tag"])
        if rumor['cover'].startswith("//jiaozhen"):
            coverimg = "https:" + rumor['cover']
        else:
            coverimg = rumor['cover']
        item_loader.add_value("coverimg", coverimg)
        rumor_item = item_loader.load_item()
        yield rumor_item

