import requests
import re
from datetime import datetime
s = datetime.now()
resp=requests.get('https://m.weibo.cn/detail/4490761267109144')
# a = resp.content.decode("utf-8").replace('\n','')
a = resp.text
# b = '\n"stream_url": "http://f.video.weibocdn.com/j0Nu8J0zlx07ChOqCMs0010412004kXY0E010.mp4?label=mp4_ld&template=360x360.25.0&trans_finger=40a32e8439c5409a63ccf853562a60ef&Expires=1589090120&ssig=1%2FYEUKI39u&KID=unistore,video",'
# print(a)
matchObj = re.match('.*"stream_url": "(.*?)"', a, re.S)
if matchObj:
    print(matchObj.group(1))
    # print(matchObj.group(2))
e = datetime.now()
print((e-s).total_seconds())

