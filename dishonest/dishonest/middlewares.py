# -*- coding: utf-8 -*-
import random
import requests
from redis import StrictRedis
import pickle

from dishonest.dishonest.settings import USER_AGENTS, REDIS_URL
from dishonest.dishonest.settings import REDIS_COOKIES_KEY, COOKIES_KEY, COOKIES_PROXY_KEY, COOKIES_USER_AGENT_KEY

from dishonest.dishonest.spiders.gsxt import GsxtSpider

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
"""
实现随机User-Agent下载器中间
    1. 准备User-Agent列表
    2. 定义RandomUserAgent类
    3. 实现process_request方法, 设置随机的User-Agent
"""


class RandomUserAgent(object):

    def process_request(self, request, spider):
        # 如果spider是公示系统爬虫, 就直接跳过
        if isinstance(spider, GsxtSpider):
            return None

        #  3. 实现process_request方法, 设置随机的User-Agent
        request.headers['User-Agent'] = random.choice(USER_AGENTS)

        return None

"""
实现代理IP下载器中间件
    1. 定义ProxyMiddleware类
    2. 实现process_request方法, 设置代理IP
"""

class ProxyMiddleware(object):

    def process_request(self, request, spider):
        # 实现process_request方法, 设置代理IP
        # 如果spider是公示系统爬虫, 就直接跳过
        if isinstance(spider, GsxtSpider):
            return None

        # 1. 获取协议头
        protocol = request.url.split('://')[0]
        # 2. 构建代理IP请求的URL
        proxy_url = 'http://localhost:16888/random?protocol={}'.format(protocol)
        # 3. 发送请求, 获取代理IP
        response = requests.get(proxy_url)
        # 4. 把代理IP设置给request.meta['proxy']
        request.meta['proxy'] = response.content.decode()

        return None

"""
实现公示系统中间类:
步骤
    1. 实现process_request方法, 从Redis中随机取出Cookie来使用, 关闭页面重定向.
    2. 实现process_response方法, 如果响应码不是200 或 没有内容重试
"""

class GsxtCookieMiddleware(object):

    def __init__(self):
        """建立Redis数据库连接"""
        self.redis = StrictRedis.from_url(REDIS_URL)

    def process_request(self, request, spider):
        """从Redis中随机取出Cookie来使用, 关闭页面重定向."""
        count = self.redis.llen(REDIS_COOKIES_KEY)
        random_index = random.randint(0, count-1)
        cookie_data = self.redis.lindex(REDIS_COOKIES_KEY, random_index)
        # 反序列化, 把二进制转换为字典
        cookie_dict = pickle.loads(cookie_data)

        # 把cookie信息设置request
        request.headers['User-Agent'] = cookie_dict[COOKIES_USER_AGENT_KEY]
        # 设置请求代理IP
        request.meta['proxy'] = cookie_dict[COOKIES_PROXY_KEY]
        # 设置cookie信息
        request.cookies = cookie_dict[COOKIES_KEY]
        # 设置不要重定向
        request.meta['dont_redirect'] = True

    def process_response(self, request, response, spider):
        """如果响应码不是200 或 没有内容重试"""
        # print(response.status)
        if response.status != 200 or response.body == b'':
            # 备份请求
            req = request.copy()
            # 设置请求不过滤
            req.dont_filter = True
            # 把请求交给引擎
            return req

        return response