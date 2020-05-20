from scrapy.cmdline import execute

import sys
import os

# print(os.path.dirname(os.path.abspath(__file__)))

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#
execute(["scrapy","crawl","weibo"])

# import re
# json={"created_at": "Fri Mar 27 23:14:36 +0800 2020".replace("+0800 ","")}
# import time
# test = time.strptime(json["created_at"])
# print(test)
# print(time.strftime("%Y-%m-%d %H:%M:%S",test) )
