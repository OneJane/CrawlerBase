#coding:utf-8
import os
import sys
import time

from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute('scrapy crawl jd_category'.split())
execute('scrapy crawl jd_product'.split())
# execute('scrapy crawl goods'.split())
# execute('scrapy crawl Mconditions'.split())
# execute('scrapy crawlall'.split())
