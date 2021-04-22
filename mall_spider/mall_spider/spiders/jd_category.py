# -*- coding: utf-8 -*-
import scrapy
import json
from mall_spider.items import Category


class JdCategorySpider(scrapy.Spider):
    name = 'jd_category'
    allowed_domains = ['3.cn']
    start_urls = ['https://dc.3.cn/category/get']

    def parse(self, response):
        # print(response.body.decode('GBK'))
        result = json.loads(response.body.decode('GBK'))
        datas = result['data']
        # 遍历数据列表
        for data in datas:

            item = Category()

            b_category = data['s'][0]
            b_category_info = b_category['n']
            # print('大分类: {}'.format(b_category_info))
            item['b_category_name'], item['b_category_url'] = self.get_category_name_url(b_category_info)

            # 中分类信息列表
            m_category_s = b_category['s']
            # 遍历中分类列表
            for m_category in m_category_s:
                # 中分类信息
                m_category_info = m_category['n']
                # print('中分类: {}'.format(m_category_info))
                item['m_category_name'], item['m_category_url'] = self.get_category_name_url(m_category_info)

                # 小分类数据列表
                s_category_s = m_category['s']
                for s_category in s_category_s:
                    s_category_info = s_category['n']
                    # print('小分类: {}'.format(s_category_info))
                    item['s_category_name'], item['s_category_url'] = self.get_category_name_url(s_category_info)
                    # print(item)
                    # 把数据交给引擎
                    yield item

    def get_category_name_url(self, category_info):
        """
        根据分类信息, 提取名称和URL
        :param category_info:  分类信息
        :return: 分类的名称和URL
        分析数据格式(三类数据格式)
        - book.jd.com/library/science.html|科学技术||0
        - 1713-3287|计算机与互联网||0
          - Https://channel.jd.com/{}.html
        - 9987-12854-12856|屏幕换新||0
          - Https://list.jd.com/list.html?cat={}
          - 把 - 替换为逗号, 然后填充到占位的地方.
        """
        category = category_info.split('|')
        # 分类URL
        category_url = category[0]
        # 分类名称
        category_name = category[1]

        # 处理第一类分类URL
        if category_url.count('jd.com') == 1:
            # URL进行补全
            category_url = 'https://' + category_url
        elif category_url.count('-') == 1:
            # 1713-3287|计算机与互联网||0
            category_url = 'https://channel.jd.com/{}.html'.format(category_url)
        else:
            # 9987-12854-12856|屏幕换新||0
            # 把URL中 `-` 替换为 `,`
            category_url = category_url.replace('-', ',')
            # 补全URL
            category_url = 'https://list.jd.com/list.html?cat={}'.format(category_url)

        # 返回类别的名称 和 URL
        return category_name, category_url

