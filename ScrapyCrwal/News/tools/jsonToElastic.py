from datetime import datetime
import json
import time
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, connections

# Define a default Elasticsearch client
from models.es_types import WeiboType

# es = connections.create_connection(hosts=['localhost'])
es = connections.create_connection(hosts=["http://119.3.52.214:9200"], http_auth=("elastic:jin821950!"))


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

def save2es(value):
    weibo = WeiboType()
    weibo.text = value.get("text", "")
    weibo.created_at = value['created_at']
    weibo.user = value['user']
    weibo.pics = value.get('pics',[])
    weibo.reposts_count = value.get('reposts_count', 0)
    weibo.comments_count = value.get('comments_count', 0)
    weibo.attitudes_count = value.get('attitudes_count', 0)
    weibo.video_info = value.get('video_info',{})

    weibo.meta.id = value['id']

    weibo.suggest = gen_suggestion(WeiboType.Index.name, ((weibo.text, 10),))

    weibo.save()
    return

if __name__ == '__main__':
    loseCnt = []
    with open('/Users/vium/PycharmProjects/Search/Crwal/News/News.json', 'r') as f:
        # next(f)
        line = f.readline()
        cnt = 0
        while line :
            cnt += 1
            s = json.loads(line)
            try:
                save2es(s)
            except Exception as e:
                loseCnt.append(cnt)
                print("第%s个载入失败，Id：%s" % (cnt, s["id"]))
                print(e)
                pass
            else:
                print("第%s个载入成功，Id：%s" % (cnt, s["id"]))
            line = f.readline()
    print(len(loseCnt))
    print(loseCnt)