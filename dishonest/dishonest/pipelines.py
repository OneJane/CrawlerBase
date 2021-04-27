# -*- coding: utf-8 -*-
import pymysql
from dishonest.dishonest.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
"""
实现管道类

步骤:
1. 在open_spider中, 建立数据库连接, 获取操作的数据的cursor
2. 在close_spider中, 关闭cursor,关闭数据库连接
3. 在process_item中, 如果数据不存, 保存数据;
"""


class DishonestPipeline(object):

    def open_spider(self, spider):
        """
        1. 在open_spider中, 建立数据库连接, 获取操作的数据的cursor
        """
        # 建立数据库连接
        self.connection = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, db=MYSQL_DB,
                                          user=MYSQL_USER, password=MYSQL_PASSWORD)
        # 获取操作数据的cursor
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        """
        2. 在close_spider中, 关闭cursor,关闭数据库连接
        """
        # 1. 关闭cursor
        self.cursor.close()
        # 2. 关闭数据库连接
        self.connection.close()

    def process_item(self, item, spider):
        """
        3. 在process_item中, 如果数据不存, 保存数据;
        """
        # 如果是自然人, 根据证件号进行判断
        # 如果是企业/组织: 企业名称 和 区域进行判断
        # 如何判断是企业还是自然人? 如果年龄为0就是企业, 否则就是自然人
        if item['age'] == 0:
            # 如果是企业, 根据 企业名称 和 区域进行判断 是否重复
            select_count_sql = "SELECT COUNT(1) from dishonest WHERE name = '{}' and area = '{}'". \
                format(item['name'], item['area'])
        else:
            card_num = item['card_num']
            # 如果证件号是18位, 那么就倒数第7到倒数第4位(不包含), 三个数字使用了**** 替换掉
            if len(card_num) == 18:
                card_num = card_num[:-7] + '****' + card_num[-4:]
                # print(card_num)
                # print(len(card_num))
                # 为了保护失信人隐私 和 数据格式一致性, 把修改后的数据赋值回去
                item['card_num'] = card_num

            # 否则就是自然人
            select_count_sql = "SELECT COUNT(1) from dishonest WHERE card_num = '{}'".format(item['card_num'])

        # 执行查询SQL
        self.cursor.execute(select_count_sql)
        # 获取查询结果
        count = self.cursor.fetchone()[0]

        if count == 0:
            keys, values = zip(*dict(item).items())
            # 如果没有数据, 就插入数据
            insert_sql = 'INSERT INTO dishonest ({}) VALUES ({})'.format(
                ','.join(keys),
                ','.join(['%s'] * len(values))
            )
            # 执行SQL
            self.cursor.execute(insert_sql, values)
            # 提交事务
            self.connection.commit()
            spider.logger.info('插入数据')
        else:
            # 否则就重复了
            spider.logger.info('数据重复')

        return item