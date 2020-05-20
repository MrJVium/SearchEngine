from django.shortcuts import render
from django.views.generic.base import View
from search.models import RumorType, WeiboType, NewsType, JsonModel
from django.http import HttpResponse, JsonResponse
from elasticsearch import Elasticsearch
import json
from datetime import datetime
import redis
import requests
import re
import math
import jieba
# Create your views here.

client = Elasticsearch(hosts=["http://119.3.52.214:9200"], http_auth=("elastic:jin821950!"))
redis_cli = redis.StrictRedis(host="119.3.52.214", db=0, password="jin821950!")
stopwords = [line.strip() for line in open('./stopwords.txt').readlines()]

class IndexView(View):
    def get(self, request):
        topbn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = []
        for i in topbn_search:
            i = str(i, 'utf-8')
            topn_search.append(i)
        return render(request, "index.html", {"topn_search":topn_search,})

class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('keyword', '')
        stype = request.GET.get('type', 'news')
        EsType = {'news': NewsType.search(), 'weibo': WeiboType.search(), 'rumor': RumorType.search()}
        sugAttr = {'news': 'title', 'rumor': 'title', 'weibo': 'text'}
        if key_words:
            re_datas = []
            s = EsType[stype]
            s = s.suggest('My_SUGGESTION', key_words, completion={
                'field': 'suggest', 'fuzzy': {
                    'fuzziness': 2
                },
                'size': 10
            })
            suggestions = s.execute()
            for match in suggestions.suggest.My_SUGGESTION[0].options:
                source = match._source
                re_datas.append(self.seg_depart(source[sugAttr[stype]]))
            # return HttpResponse(json.dumps(re_datas), content_type='application/json')
            return JsonResponse(re_datas, safe=False)

    def seg_depart(self, sentence):
        sentence_depart = jieba.cut(sentence.strip(), cut_all=False)
        outstr = ''
        for word in sentence_depart:
            if word not in stopwords:
                if word != '\t':
                    outstr += word
                    outstr += " "
        return outstr

class SearchWeiBoView(View):
    def get(self, request):
        key_words = request.GET.get("keyword", "")
        stime = request.GET.get("starttime", "1970-01-01T00:00:00")
        etime = request.GET.get("endtime", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        limit = request.GET.get("limit", 10)
        page = request.GET.get('page', 1)
        if key_words:
            redis_cli.zincrby("searchWeibo_keywords_set", 1, key_words)
        topbn_search = redis_cli.zrevrangebyscore("searchWeibo_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = []
        for i in topbn_search:
            i = str(i, 'utf-8')
            topn_search.append(i)
        try:
            page = int(page)
        except:
            page = 1
        start_time = datetime.now()
        try:
            response = client.search(
            index="weibo",
            body={
                  "query": {
                    "function_score": {
                      "query": {
                        "bool": {
                                "must": [
                                    {
                                      "range": {
                                                        "created_at": {
                                                            "gte": stime,
                                                            "lte": etime
                                                        }
                                                    }
                                    },
                                    {
                                        "multi_match": {
                                            "query": key_words,
                                            "fields": ["text", "user.screen_name"]
                                        }
                                    }
                                ],
                                "must_not": [],
                                "should": []
                            }
                      },
                      "functions": [
                        {
                          "field_value_factor": {
                            "field": ["attitudes_count"],
                            "modifier": "log1p",
                            "factor": 0.3
                          }
                        },
                        {
                          "field_value_factor": {
                            "field": ["reposts_count"],
                            "modifier": "log1p",
                            "factor": 0.5
                          }

                        },
                        {
                          "field_value_factor": {
                            "field": ["comments_count"],
                            "modifier": "log1p",
                            "factor": 0.2
                          }

                        }

                      ]
                    }
                  },
                    "from":(page-1)*limit,
                    "size":limit,
                    "highlight":{
                        "pre_tags": ["<span class='highlight'>"],
                        "post_tags": ["</span>"],
                        "fields": {
                            "user.screen_name":{},
                            "text":{}
                        }
                    }
                }
            )
            end_time = datetime.now()
            last_time = (end_time - start_time).total_seconds()
            total_nums = response['hits']['total']['value']
            hit_list = []
            for hit in response['hits']['hits']:
                data = {}
                data['created_at'] = hit['_source']['created_at']
                data['reposts_count'] = hit['_source']['reposts_count']
                data['comments_count'] = hit['_source']['comments_count']
                data['attitudes_count'] = hit['_source']['attitudes_count']
                data['pics'] = hit['_source'].get('pics', [])
                data['user'] = hit['_source']['user']

                if "text" in hit.get('highlight', {}):
                    data["text"] = ''.join(hit['highlight']['text'])
                else:
                    data['text'] = ''.join(hit['_source']['text'])
                if "user.screen_name" in hit.get('highlight', {}):
                    data["user"]["screen_name"] = ''.join(hit['highlight']['user.screen_name'])

                data['url'] = "https://m.weibo.cn/detail/"+hit['_id']
                data['score'] = math.sqrt(hit['_score'])

                if "video_info" in hit['_source']:
                    data['video_info'] = hit['_source']['video_info']
                    data['video_info']['media_info'] = {"stream_url": self.videoUrl(data['url']), "duration": hit['_source']['video_info']['media_info']['duration'] }

                hit_list.append(data)

            return JsonResponse(JsonModel.success({"timespent": last_time,
                                                   "totalnum": total_nums,
                                                   "data": hit_list,
                                                   "topSearch": topn_search
                                                   }))
        except:
            return JsonResponse(JsonModel.failed({"data": None}))

    def videoUrl(self, url):
        resp = requests.get(url)
        a = resp.text
        matchObj = re.match('.*"stream_url": "(.*?)"', a, re.S)
        if matchObj:
            return(matchObj.group(1))
        resp.close()



class SearchNewsView(View):
    def get(self, request):
        key_words = request.GET.get('keyword', "")
        stime = request.GET.get("starttime", "1970-01-01T00:00:00")
        etime = request.GET.get("endtime", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        limit = request.GET.get("limit", 10)
        page = request.GET.get('page', 1)
        provinceName = request.GET.get('provinceName', "")
        if key_words:
            redis_cli.zincrby("searchNews_keywords_set", 1, key_words)
        topbn_search = redis_cli.zrevrangebyscore("searchNews_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = []
        for i in topbn_search:
            i = str(i, 'utf-8')
            topn_search.append(i)
        try:
            page = int(page)
        except:
            page = 1
        start_time = datetime.now()
        try:
            if provinceName:
                response = client.search(
                    index="news",
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "range": {
                                            "pubDate": {
                                                "gte": stime,
                                                "lte": etime
                                            }
                                        }
                                    },
                                    {
                                        "multi_match": {
                                            "query": key_words,
                                            "fields": ["title", "summary", "infoSource", "provinceName"]
                                        }
                                    },
                                    {
                                        "match":{
                                            "provinceName": provinceName
                                        }
                                    }
                                ],
                                "must_not": [],
                                "should": []
                            }
                        },
                        "from": (page - 1) * limit,
                        "size": limit,
                        "highlight": {
                            "pre_tags": ['<span class="highlight">'],
                            "post_tags": ['</span>'],
                            "fields": {
                                "title": {},
                                "summary": {},
                                "infoSource": {},
                                "provinceName": {}
                            }
                        }
                    }
                )
            else:
                response = client.search(
                    index="news",
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "range": {
                                            "pubDate": {
                                                "gte": stime,
                                                "lte": etime
                                            }
                                        }
                                    },
                                    {
                                        "multi_match": {
                                            "query": key_words,
                                            "fields": ["title", "summary", "infoSource", "provinceName"]
                                        }
                                    }
                                ],
                                "must_not": [],
                                "should": []
                            }
                        },
                        "from": (page - 1) * limit,
                        "size": limit,
                        "highlight": {
                            "pre_tags": ['<span class="highlight">'],
                            "post_tags": ['</span>'],
                            "fields": {
                                "title": {},
                                "summary": {},
                                "infoSource": {},
                                "provinceName": {}
                            }
                        }
                    }
                )
            end_time = datetime.now()
            last_time = (end_time - start_time).total_seconds()
            total_nums = response['hits']['total']['value']
            hit_list = []
            for hit in response['hits']['hits']:
                data = {}
                data = hit['_source']
                data.pop('suggest')
                if "title" in hit.get('highlight', {}):
                    data['title'] = ''.join(hit['highlight']['title'])
                if "summary" in hit.get('highlight', {}):
                    data['summary'] = ''.join(hit['highlight']['summary'])
                if "infoSource" in hit.get('highlight', {}):
                    data['infoSource'] = ''.join(hit['highlight']['infoSource'])
                if "provinceName" in hit.get('highlight', {}):
                    data['provinceName'] = ''.join(hit['highlight']['provinceName'])

                data['score'] = hit['_score']
                hit_list.append(data)

            return JsonResponse(JsonModel.success({"timespent": last_time,
                                                   "totalnum": total_nums,
                                                   "data": hit_list,
                                                   "topSearch": topn_search
                                                   }))
        except:
            return JsonResponse(JsonModel.failed({"data": None}))



class SearchRumorView(View):
    def get(self, request):
        rtype = request.GET.get('type', 4)
        key_words = request.GET.get("keyword", "")
        stime = request.GET.get("starttime", "1970-01-01T00:00:00")
        etime = request.GET.get("endtime", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        limit = request.GET.get("limit", 10)
        page = request.GET.get('page', 1)

        if key_words:
            redis_cli.zincrby("searchRumor_keywords_set", 1, key_words)
        topbn_search = redis_cli.zrevrangebyscore("searchRumor_keywords_set", "+inf", "-inf", start=0, num=5)
        topn_search = []
        for i in topbn_search:
            i = str(i, 'utf-8')
            topn_search.append(i)
        try:
            page = int(page)
        except:
            page = 1
        start_time = datetime.now()
        try:
            if rtype == 4:
                response = client.search(
                    index="rumor",
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "range": {
                                            "date": {
                                                "gte": stime,
                                                "lte": etime
                                            }
                                        }
                                    },
                                    {
                                        "multi_match": {
                                            "query": key_words,
                                            "fields": ["text", "title","abstract","author","tag"]
                                        }
                                    }
                                ],
                                "must_not": [],
                                "should": []
                            }
                        },
                        "from": (page - 1) * limit,
                        "size": limit,
                        "highlight": {
                            "pre_tags": ['<span class="highlight">'],
                            "post_tags": ['</span>'],
                            "fields": {
                                "title": {},
                                "text": {},
                                "abstract": {},
                                "author": {},
                                "tag": {}
                            }
                        }
                    }
                )
            else:
                rtype = int(rtype)
                result = ['假','疑','真']
                response = client.search(
                    index="rumor",
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "range": {
                                            "date": {
                                                "gte": stime,
                                                "lte": etime
                                            }
                                        }
                                    },
                                    {
                                        "multi_match": {
                                            "query": key_words,
                                            "fields": ["text", "title", "abstract", "author", "tag"]
                                        }
                                    },
                                    {
                                        "match":{
                                            "result": result[rtype]
                                        }
                                    }
                                ],
                                "must_not": [],
                                "should": []
                            }
                        },
                        "from": (page - 1) * limit,
                        "size": limit,
                        "highlight": {
                            "pre_tags": ['<span class="highlight">'],
                            "post_tags": ['</span>'],
                            "fields": {
                                "title": {},
                                "text": {},
                                "abstract": {},
                                "author": {},
                                "tag": {}
                            }
                        }
                    }
                )
            end_time = datetime.now()
            last_time = (end_time - start_time).total_seconds()
            total_nums = response['hits']['total']['value']
            hit_list = []
            for hit in response['hits']['hits']:
                data = {}
                data = hit['_source']
                data.pop('suggest')

                if "text" in hit.get('highlight', {}):
                    data["text"] = ''.join(hit['highlight']['text'])
                if "title" in hit.get('highlight', {}):
                    data["title"] = ''.join(hit['highlight']['title'])
                if "abstract" in hit.get('highlight', {}):
                    data["abstract"] = ''.join(hit['highlight']['abstract'])
                if "author" in hit.get('highlight', {}):
                    data["author"] = ''.join(hit['highlight']['author'])
                if "tag" in hit.get('highlight', {}):
                    data["tag"] = ''.join(hit['highlight']['tag'])

                data['url'] = "https://vp.fact.qq.com/article?id=" + hit['_id']
                data['score'] = hit['_score']

                hit_list.append(data)

            return JsonResponse(JsonModel.success({"timespent": last_time,
                                                   "totalnum": total_nums,
                                                   "data": hit_list,
                                                   "topSearch": topn_search
                                                   }))
        except:
            return JsonResponse(JsonModel.failed({"data": None}))


class SearchAreaView(View):
    def get(self, request):
        areaName = request.GET.get("areaName", "")
        stime = request.GET.get("starttime", self.updated())
        etime = request.GET.get("endtime", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        limit = request.GET.get("limit", 10)
        page = request.GET.get('page', 1)

        try:
            page = int(page)
        except:
            page = 1
        start_time = datetime.now()
        response = client.search(
            index="area",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "updateTime": {
                                        "gte": stime,
                                        "lte": etime
                                    }
                                }
                            },
                            {
                                "multi_match": {
                                    "query": areaName,
                                    "fields": ["continentName", "countryName", "provinceName", "cityName"]
                                }
                            }
                        ],
                        "must_not": [],
                        "should": []
                    }
                },
                "from": (page - 1) * limit,
                "size": limit
            }
        )
        end_time = datetime.now()
        last_time = (end_time - start_time).total_seconds()
        total_nums = response['hits']['total']['value']
        hit_list = []
        for hit in response['hits']['hits']:
            data = {}
            data = hit['_source']
            data.pop('suggest')
            hit_list.append(data)
        return JsonResponse(JsonModel.success({"timespent": last_time,
                                                   "totalnum": total_nums,
                                                   "data": hit_list
                                                   }))


    def updated(self):
        response = client.search(
            index="area",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "updateTime": {
                                        "lt": "2020-05-11"
                                    }
                                }
                            }
                        ],
                        "must_not": [],
                        "should": []
                    }
                },
                "from": 0,
                "size": 1,
                "sort": {"updateTime": {"order": "desc"}}
            }
        )
        updateTime = response['hits']['hits'][0]['_source']['updateTime']
        return updateTime[:11]+"00:00:00"

class SearchOverallView(View):
    def get(self, request):
        stime = request.GET.get("starttime", self.updated())
        etime = request.GET.get("endtime", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        limit = request.GET.get("limit", 10)
        page = request.GET.get('page', 1)

        try:
            page = int(page)
        except:
            page = 1
        try:
            start_time = datetime.now()
            response = client.search(
                index="overall",
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "updateTime": {
                                            "gte": stime,
                                            "lte": etime
                                        }
                                    }
                                }
                            ],
                            "must_not": [],
                            "should": []
                        }
                    },
                    "from": (page - 1) * limit,
                    "size": limit
                }
            )
            end_time = datetime.now()
            last_time = (end_time - start_time).total_seconds()
            total_nums = response['hits']['total']['value']
            hit_list = []
            for hit in response['hits']['hits']:
                data = {}
                data = hit['_source']
                hit_list.append(data)
            return JsonResponse(JsonModel.success({"timespent": last_time,
                                                   "totalnum": total_nums,
                                                   "data": hit_list
                                                   }))
        except:
            return JsonResponse(JsonModel.failed({"data": None}))


    def updated(self):
        response = client.search(
            index="overall",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "updateTime": {
                                        "lt": "2020-05-11"
                                    }
                                }
                            }
                        ],
                        "must_not": [],
                        "should": []
                    }
                },
                "from": 0,
                "size": 1,
                "sort": {"updateTime": {"order": "desc"}}
            }
        )
        updateTime = response['hits']['hits'][0]['_source']['updateTime']
        return updateTime[:11]+"00:00:00"

class SearchNewsByDayView(View):
    def get(self, request):
        date = request.GET.get("date", "2020-01-24")
        response = client.search(
            index="news",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "pubDate": {
                                        "gte": date,
                                        "lte": date
                                    }
                                }
                            }
                        ],
                        "must_not": [],
                        "should": []
                    }
                },
                "from": 0,
                "size": 20
            }
        )
        total_nums = response['hits']['total']['value']
        hit_list = []
        for hit in response['hits']['hits']:
            data = {}
            data = hit['_source']
            data.pop('suggest')

            data['score'] = hit['_score']
            hit_list.append(data)

        return JsonResponse(JsonModel.success({
                                               "totalnum": total_nums,
                                               "data": hit_list,
                                               }))