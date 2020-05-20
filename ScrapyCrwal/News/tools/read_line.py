import codecs
import json
import redis
pool = redis.ConnectionPool(host="119.3.52.214", port="6379", db=0, password="jin821950!")
db = redis.StrictRedis(connection_pool=pool)
jsonList = []
#
with open('../Comments.json', 'r') as f:
    line = f.readline()
    while line:
        s = json.loads(line)
        if db.sadd("Comments", s["id"]) == 1:
            jsonList.append(s)
        line = f.readline()
#
# with open(r'data.json','w',encoding='utf-8') as f:
#     f.write(json.dumps(jsonList, ensure_ascii=False))

file = codecs.open(r"../Comments.json", "a", encoding="utf-8")
for i in jsonList:
    lines = json.dumps(i, ensure_ascii=False) + '\n'
    file.write(lines)
file.close()