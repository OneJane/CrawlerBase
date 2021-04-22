# -*- coding: utf-8 -*-
import scrapy
import json
from jsonpath import jsonpath
from scrapy_redis.spiders import RedisSpider
import pickle

from mall_spider.items import Product

"""

scrapy_redis: 分布式爬虫
1. 修改爬虫类
- 修改继承关系: 继承RedisSpider
- 指定redis_key
- 把重写start_requests 改为 重写 make_request_from_data

"""

# 1. 修改继承关系: 继承RedisSpider
class JdProductSpider(RedisSpider):
    name = 'jd_product'
    allowed_domains = ['jd.com', '3.cn']
    # 2. 指定redis_key, 用于指定起始URL列表,在Redis数据库中key
    # 不需要start_urls
    redis_key = 'jd_product:category'

    # 3.把重写start_requests 改为 重写 make_request_from_data
    # def start_requests(self):
    #     """重写start_requests方法, 根据分类信息构建列表页的请求"""
    #     category = {"b_category_name" : "家用电器",
    #                 "b_category_url" : "https://jiadian.jd.com",
    #                 "m_category_name" : "电视",
    #                 "m_category_url" : "https://list.jd.com/list.html?cat=737,794,798",
    #                 "s_category_name" : "曲面电视",
    #                 "s_category_url" : "https://list.jd.com/list.html?cat=737,794,798&ev=4155_92263&sort=sort_rank_asc&trans=1&JL=3_%E7%94%B5%E8%A7%86%E7%B1%BB%E5%9E%8B_%E6%9B%B2%E9%9D%A2#J_crumbsBar" }
    #
    #     # 根据小分类的URL, 构建列表页的请求
    #     yield scrapy.Request(category['s_category_url'], callback=self.parse, meta={'category': category})

    def make_request_from_data(self, data):
        """
        根据redis中读取的分类信息的二进制数据, 构建请求
        :param data: 分类信息的二进制数据
        :return: 根据小分类URL, 构建的请求对象
        """
        # 把分类信息的二进制数据 转换为字典
        category = pickle.loads(data)
        # 根据小分类的URL, 构建列表页的请求
        # 注意: 要使用return来返回一个请求, 不能使用yield
        return scrapy.Request(category['s_category_url'], callback=self.parse, meta={'category': category})

    def parse(self, response):

        category = response.meta['category']
        # print(category)
        # 解析列表页, 提取商品的skuid
        sku_ids = response.xpath('//div[contains(@class, " j-sku-item")]/@data-sku').extract()
        for sku_id in sku_ids:
            # 创建Product, 用于保存商品数据
            item = Product()
            # 设置商品类别
            item['product_category'] = category
            item['product_sku_id'] = sku_id
            # 构建商品基本的信息请求 手机端抓包
            product_base_url = 'https://cdnware.m.jd.com/c1/skuDetail/apple/7.3.0/{}.json'.format(sku_id)
            yield scrapy.Request(product_base_url, callback=self.parse_product_base, meta={'item': item})

        # 获取下一页的URL
        next_url = response.xpath('//a[@class="pn-next"]/@href').extract_first()
        if next_url:
            # 补全URL
            next_url = response.urljoin(next_url)
            # print(next_url)
            # 构建下一页的请求
            yield scrapy.Request(next_url, callback=self.parse, meta={'category': category})


    def parse_product_base(self, response):
        # 取出传递过来的数据
        item = response.meta['item']
        # print(item)
        # print(response.text)
        # 把json字符串, 转换为字典
        result = json.loads(response.text)
        # 提取数据
        # 1. product_name: 商品名称
        item['product_name'] = result['wareInfo']['basicInfo']['name']
        # 2. product_img_url: 商品图片URL
        item['product_img_url'] = result['wareInfo']['basicInfo']['wareImage'][0]['small']
        # 3. product_book_info: 图书信息, 作者,出版社
        item['product_book_info'] = result['wareInfo']['basicInfo']['bookInfo']
        # 4. product_option: 商品选项
        color_size = jsonpath(result, '$..colorSize')
        if color_size:
            # 注意: colorSize:值是列表, 而jsonpath返回列表, color_size是两层列表
            color_size = color_size[0]
            product_option = {}
            for option in color_size:
                title = option['title']
                value = jsonpath(option, '$..text')
                product_option[title] = value
            item['product_option'] = product_option

        # 5. product_shop: 商品店铺
        shop = jsonpath(result, '$..shop')
        if shop:
            shop = shop[0]
            if shop:
                item['product_shop'] = {
                    'shop_id': shop['shopId'],
                    'shop_name': shop['name'],
                    'shop_score': shop['score'],
                }
            else:
                item['product_shop'] = {
                    'shop_name': '京东自营',
                }
        # 6. product_category_id :  商品类别ID
        item['product_category_id'] = result['wareInfo']['basicInfo']['category']
        # category: "9987;653;655" => 需要 ';' 替换为 ','
        item['product_category_id'] = item['product_category_id'].replace(';', ',')
        # print(item)
        # 准备促销信息的URL
        ad_url = 'https://cd.jd.com/promotion/v2?skuId={}&area=1_72_4137_0&cat={}'\
            .format(item['product_sku_id'], item['product_category_id'])
        # 构建促销信息的请求
        yield scrapy.Request(ad_url, callback=self.parse_product_ad, meta={'item': item})

    def parse_product_ad(self, response):
        item = response.meta['item']
        # print(item)
        # print(response.body.decode('GBK'))
        # 把数据转换为字典
        result = json.loads(response.body.decode('GBK'))
        # product_ad : 商品促销
        item['product_ad'] = jsonpath(result, '$..ad')[0] if jsonpath(result, '$..ad') else ''
        # print(item)
        # 构建评价信息请求
        comments_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'.\
            format(item['product_sku_id'])
        yield scrapy.Request(comments_url, callback=self.parse_product_comments, meta={'item': item})

    def parse_product_comments(self, response):
        item = response.meta['item']
        # print(item)
        # print(response.text)

        # 解析商品评价信息
        result = json.loads(response.text)
        # 1. product_comments : 商品评论数量
        # 2. 评价数量, 好评数量, 差评数量, 好评率
        item['product_comments'] = {
            'CommentCount': jsonpath(result, '$..CommentCount')[0],
            'GoodCount': jsonpath(result, '$..GoodCount')[0],
            'PoorCount': jsonpath(result, '$..PoorCount')[0],
            'GoodRate': jsonpath(result, '$..GoodRate')[0],
        }
        # print(item)
        # 构建价格请求
        price_url = 'https://p.3.cn/prices/mgets?skuIds=J_{}'.format(item['product_sku_id'])
        yield scrapy.Request(price_url, callback=self.parse_product_price, meta={'item': item})

    def parse_product_price(self, response):
        item = response.meta['item']
        # print(response.text)
        result = json.loads(response.text)
        # product_price: 商品价格
        item['product_price'] = result[0]['p']
        # print(item)
        # 把商品数据交给引擎
        yield item
