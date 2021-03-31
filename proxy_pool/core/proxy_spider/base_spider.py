import requests
from utils.http import get_request_headers
from lxml import etree
from domain import Proxy

"""
8.3 实现通用爬虫
目标: 实现可以指定不同URL列表, 分组的XPATH和详情的XPATH, 从不同页面上提取代理的IP,端口号和区域的通用爬虫;
步骤:

1. 在base_spider.py文件中,定义一个BaseSpider类, 继承object
2. 提供三个类成员变量:
    urls: 代理IP网址的URL的列表
    group_xpath: 分组XPATH, 获取包含代理IP信息标签列表的XPATH
    detail_xpath: 组内XPATH, 获取代理IP详情的信息XPATH, 格式为: {'ip':'xx', 'port':'xx', 'area':'xx'}
3. 提供初始方法, 传入爬虫URL列表, 分组XPATH, 详情(组内)XPATH
4. 对外提供一个获取代理IP的方法
    4.1 遍历URL列表, 获取URL
    4.2 根据发送请求, 获取页面数据
    4.3 解析页面, 提取数据, 封装为Proxy对象
    4.4 返回Proxy对象列表
"""

# 1. 在base_spider.py文件中,定义一个BaseSpider类, 继承object
class BaseSpider(object):

    # 2. 提供三个类成员变量:
    # urls: 代理IP网址的URL的列表
    urls = []
    # group_xpath: 分组XPATH, 获取包含代理IP信息标签列表的XPATH
    group_xpath = ''
    # detail_xpath: 组内XPATH, 获取代理IP详情的信息XPATH, 格式为: {'ip':'xx', 'port':'xx', 'area':'xx'}
    detail_xpath = {}

    # 3. 提供初始方法, 传入爬虫URL列表, 分组XPATH, 详情(组内)XPATH
    def __init__(self, urls=[], group_xpath='', detail_xpath={}):

        if urls:
            self.urls = urls

        if group_xpath:
            self.group_xpath = group_xpath

        if detail_xpath:
            self.detail_xpath = detail_xpath

    def get_page_from_url(self, url):
        """根据URL 发送请求, 获取页面数据"""
        response = requests.get(url, headers=get_request_headers())
        print(url)
        print(response.status_code)
        return response.content

    def get_first_from_list(self, lis):
        # 如果列表中有元素就返回第一个, 否则就返回空串
        return lis[0] if len(lis) != 0 else ''

    def get_proxies_from_page(self, page):
        """解析页面, 提取数据, 封装为Proxy对象"""
        element = etree.HTML(page)
        # 获取包含代理IP信息的标签列表
        trs = element.xpath(self.group_xpath)
        # 遍历trs, 获取代理IP相关信息
        for tr in trs:
            ip = self.get_first_from_list(tr.xpath(self.detail_xpath['ip']))
            port = self.get_first_from_list(tr.xpath(self.detail_xpath['port']))
            area = self.get_first_from_list(tr.xpath(self.detail_xpath['area']))
            proxy = Proxy(ip, port, area=area)
            # print(proxy)
            # 使用yield返回提取到的数据
            yield proxy

    def get_proxies(self):
        # 4. 对外提供一个获取代理IP的方法
        # 4.1 遍历URL列表, 获取URL
        for url in self.urls:
            # print(url)
            # 4.2 根据发送请求, 获取页面数据
            page = self.get_page_from_url(url)
            # 4.3 解析页面, 提取数据, 封装为Proxy对象
            proxies = self.get_proxies_from_page(page)
            # 4.4 返回Proxy对象列表
            yield from proxies

if __name__ == '__main__':

    config = {
        'urls': ['http://www.ip3366.net/free/?stype=1&page={}'.format(i) for i in range(1, 4)],
        'group_xpath': '//*[@id="list"]/table/tbody/tr',
        'detail_xpath': {
            'ip':'./td[1]/text()',
            'port':'./td[2]/text()',
            'area':'./td[5]/text()'
        }
    }

    spider = BaseSpider(**config)
    for proxy in spider.get_proxies():
        print(proxy)