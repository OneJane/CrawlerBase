# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

from mall_spider.spiders.jd_category import JdCategorySpider
from mall_spider.settings import MONGODB_URL
"""
实现保存分类的Pipeline类
- open_spider方法中, 链接MongoDB数据库, 获取要操作的集合
- process_item 方法中, 向MongoDB中插入类别数据
- close_spider 方法中, 关闭MongoDB的链接
"""

class CategoryPipeline(object):

    def open_spider(self, spider):
        """当爬虫启动的时候执行1次"""
        if isinstance(spider, JdCategorySpider):
            # open_spider方法中, 链接MongoDB数据库, 获取要操作的集合
            self.client = MongoClient(MONGODB_URL)
            self.collection = self.client['jd']['category']

    def process_item(self, item, spider):
        # process_item 方法中, 向MongoDB中插入类别数据
        if isinstance(spider, JdCategorySpider):
            self.collection.insert_one(dict(item))

        return item

    def close_spider(self, spider):
        # close_spider 方法中, 关闭MongoDB的链接
        if isinstance(spider, JdCategorySpider):
            self.client.close()


"""
8.1.实现存储商品Pipeline类
 1. 在 open_spider方法, 建立MongoDB数据库连接, 获取要操作的集合
 2. 在 process_item方法, 把数据插入到MongoDB中
 3. 在close_spider方法, 关闭数据库连接
"""
from mall_spider.spiders.jd_product import JdProductSpider

class ProuctPipeline(object):

    def open_spider(self, spider):
        """当爬虫启动的时候执行"""
        if isinstance(spider, JdProductSpider):
            # open_spider方法中, 链接MongoDB数据库, 获取要操作的集合
            self.client = MongoClient(MONGODB_URL)
            self.collection = self.client['jd']['product']

    def process_item(self, item, spider):
        # process_item 方法中, 向MongoDB中插入类别数据
        if isinstance(spider, JdProductSpider):
            self.collection.insert_one(dict(item))

        return item

    def close_spider(self, spider):
        # close_spider 方法中, 关闭MongoDB的链接
        if isinstance(spider, JdProductSpider):
            self.client.close()
