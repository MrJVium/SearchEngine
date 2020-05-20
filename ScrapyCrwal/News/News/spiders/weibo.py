# -*- coding: utf-8 -*-
import random
from urllib import parse
import re
import json
import gc

import scrapy
from scrapy import Request
import requests
from selenium import webdriver
import time
from w3lib.html import remove_tags

from News.items import NewsItemLoader, WeiboNewsItem, WeiboCommentsItem

""" 
    获取Cookie
    1、在parse中，获取含18个News的Json,
    2、将status传给parse_detail解析,parse翻页
    3、parse_detail 计算出评论页数（20条每页）
    4、评论url="https://m.weibo.cn/comments/hotflow?id=4487160537677378&mid=4487160537677378&max_id_type=0"
        (1) max_id = json["data"]["max_id"]
        (2) next_url =  https://m.weibo.cn/comments/hotflow?id=4487160537677378&mid=4487160537677378&max_id=138842479257367&max_id_type=0
        (3) 坑 max_id 用过后，就会失效 （5s左右）
    5、comment_detail
"""

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['m.weibo.cn', 'passport.weibo.cn']
    start_urls = ['https://m.weibo.cn/api/feed/trendtop?containerid=102803_ctg1_600059_-_ctg1_600059']

    # """
    def start_requests(self):
        import pickle

        cookies = pickle.load(open("/Users/vium/PycharmProjects/Search/Crwal/News/cookies/weibo.cookie", "rb"))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie['value']
        #
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.keys import Keys
        chrome_option = Options()
        chrome_option.add_argument('--disable-extensions')
        # 这里的端口和上面remote-debug对应的端口一致
        chrome_option.add_experimental_option('debuggerAddress', '127.0.0.1:9222')

        browser = webdriver.Chrome(executable_path='/Users/vium/chromedriver', chrome_options=chrome_option)
        # browser.get("https://passport.weibo.cn/signin/login")
        # # #
        # # # browser.find_element_by_css_selector("input#loginName").send_keys(Keys.COMMAND + 'a')
        # time.sleep(3)
        # browser.find_element_by_css_selector("input#loginName").send_keys("13868325178")
        # # browser.find_element_by_css_selector("input#loginPassword").send_keys(Keys.COMMAND + 'a')
        # browser.find_element_by_css_selector("input#loginPassword").send_keys("jin821950")
        # browser.find_element_by_css_selector("a#loginAction").click()
        # time.sleep(10)


        # browser.get("https://m.weibo.cn/?sudaref=security.weibo.com")
        # # #
        # cookies = browser.get_cookies()
        # pickle.dump(cookies, open("/Users/vium/PycharmProjects/Search/Crwal/News/cookies/weibo.cookie", "wb"))
        # cookie_dict = {}
        # for cookie in cookies:
        #     cookie_dict[cookie["name"]] = cookie['value']
        # # #
        # time.sleep(20)
        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
    # """


    def parse(self, response):
        base_url = "https://m.weibo.cn/api/feed/trendtop?containerid=102803_ctg1_600059_-_ctg1_600059?page="
        statuses = json.loads(response.body.decode("utf-8"))["data"]["statuses"]
        for i, status in enumerate(statuses):
            if i % 3 == 0:
                time.sleep(3)
            extend_url = "https://m.weibo.cn/statuses/extend?id="
            yield Request(url=extend_url+status['id'], meta={"status": status}, callback=self.parse_detail)
        page = response.meta.get("page", 1)
        if page <= 2000:
            # if page % 10 == 0:
            #     time.sleep(3)
            yield Request(url=base_url+str(page), meta={"page": page+1},callback=self.parse)

    def parse_detail(self, response):
        status = response.meta.get("status", "")
        extend = json.loads(response.body.decode("utf-8"))
        item_loader = NewsItemLoader(item=WeiboNewsItem(), response=response)
        item_loader.add_value("id", status["id"])
        if extend["ok"] == 1:
            item_loader.add_value("text", remove_tags(extend["data"]["longTextContent"]))
        else:
            item_loader.add_value("text", remove_tags(status["text"]))
        # 图片信息
        pics = []
        for pic in status.get("pics", []):
            pics.append(pic["url"])
        # 用户信息
        user = {}
        user["id"] = status["user"]["id"]
        user["screen_name"] = status["user"]["screen_name"]
        user["profile_image_url"] = status["user"]["profile_image_url"]
        user["profile_url"] = status["user"]["profile_url"]
        # 视频信息
        video_info = {}
        if "page_info" in status and status["page_info"].get("type", "") == "video" and "media_info" in status["page_info"]:
            video_info["title"] = status["page_info"].get("title", "")
            video_info["play_count"] = status["page_info"].get("playcount", 0)
            video_info["video_orientation"] = status["page_info"].get("video_orientation", "")
            video_info["media_info"] = status["page_info"]["media_info"]
        # load Item
        item_loader.add_value("created_at", status["created_at"])
        item_loader.add_value("reposts_count", status["reposts_count"])
        item_loader.add_value("comments_count", status["comments_count"])
        item_loader.add_value("attitudes_count", status["attitudes_count"])
        item_loader.add_value("pics", pics)
        item_loader.add_value("user", user)
        item_loader.add_value("video_info", video_info)

        news_item = item_loader.load_item()
        yield news_item
        # 提取评论
        comments_url = "https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0".format(status["id"], status["mid"])
        yield Request(comments_url, callback=self.comments_detail)

    def comments_detail(self, response):
        hotflow = json.loads(response.body.decode("utf-8"))
        if hotflow["ok"] == 1:
            max_id = hotflow['data']['max_id']
            data = hotflow['data']['data']
            del hotflow
            gc.collect()
            for comment in data:
                if "text" not in comment or comment["text"] == "":
                    continue
                item_loader = NewsItemLoader(item=WeiboCommentsItem(), response=response)
                item_loader.add_value("id", comment["id"])
                item_loader.add_value("text", remove_tags(comment['text']))
                item_loader.add_value("like_count", comment["like_count"])
                item_loader.add_value("created_at", comment['created_at'])

                comment_item = item_loader.load_item()
                yield comment_item
            if max_id != 0:
                sleeptime = random.randint(5, 18)
                time.sleep(sleeptime)
                yield Request(response.url+"&max_id={}".format(max_id), callback=self.comments_detail)