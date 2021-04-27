"""
3.3. 根据需求, 定义数据数据模
步骤:
1. 定义数据模型类:DishonestItem, 继承scrapy.Item
2. 定义要抓取字段
    失信人名称
    失信人号码
    失信人年龄
    区域
    法人(企业)
    失信内容
    公布日期
    公布/执行单位
    创建日期
    更新日期
"""

import scrapy


class DishonestItem(scrapy.Item):
    # define the fields for your item here like:
    # 失信人名称
    name = scrapy.Field()
    # 失信人证件号
    card_num = scrapy.Field()
    # 失信人年龄, 企业年龄都是0
    age = scrapy.Field()
    # 区域
    area = scrapy.Field()
    # 法人(企业)
    business_entity = scrapy.Field()
    # 失信内容
    content = scrapy.Field()
    # 公布日期
    publish_date = scrapy.Field()
    # 公布/执行单位
    publish_unit = scrapy.Field()
    # 创建日期
    create_date = scrapy.Field()
    # 更新日期
    update_date = scrapy.Field()
