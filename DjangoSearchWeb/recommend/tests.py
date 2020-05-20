from django.test import TestCase
import requests
import time
# Create your tests here.
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys
chrome_option = Options()
chrome_option.add_argument('--disable-extensions')
# 这里的端口和上面remote-debug对应的端口一致
chrome_option.add_experimental_option('debuggerAddress', '127.0.0.1:9222')

# browser = webdriver.Chrome(executable_path='/Users/vium/chromedriver', chrome_options=chrome_option)
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
browser = webdriver.Chrome(executable_path='/Users/vium/chromedriver', options=options, chrome_options=chrome_option)

browser.get('http://www.nhc.gov.cn/xcs/xxgzbd/gzbd_index.shtml')
content = browser.page_source

# ul = browser.find_element_by_xpath("/html/body/div[3]/div[1]/ul")
time.sleep(3)
# session = requests.session()
# session.headers.update(
#                 {
#                     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
#                 }
#             )
# r = session.get(url='http://www.nhc.gov.cn/xcs/xxgzbd/gzbd_index.shtml')
soup = BeautifulSoup(content, 'html.parser')
a = soup.find_all('ul')
a= 1
# browser.close()