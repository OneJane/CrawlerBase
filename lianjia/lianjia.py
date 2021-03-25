import csv
import random
import time

import parsel
import requests

for page in range(1, 100 + 1):
    choice = random.randint(0, 3)
    time.sleep(choice)
    print("=" * 50)
    print('正在爬取{}页数据'.format(page))
    print("=" * 50)
    url = 'https://su.lianjia.com/ershoufang/pg{}/'.format(str(page))
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
    response = requests.get(url=url, headers=headers)
    html_data = response.text
    print(type(html_data))

    selector = parsel.Selector(html_data)
    lis = selector.css('.clear.LOGCLICKDATA')
    for li in lis:
        title = li.css('.title a::text').get()  # 标题
        address = li.css('.positionInfo a::text').getall()  # 地址
        address = ','.join(address)
        houseInfo = li.css('.houseInfo::text').get()  # 信息
        followInfo = li.css('.followInfo::text').get()  # 关注
        tags = li.css('.tag span::text').get()  # 标签
        tags = ','.join(tags)
        totalPrice = li.css('.totalPrice span::text').get() + '万'  # 总价
        unitePrice = li.css('.unitPrice span::text').get()  # 单价
        title_url = li.css('.title a::attr(href)').get()  # 标题
        print(title, address, houseInfo, followInfo, tags, totalPrice, unitePrice, title_url, sep="---")

        with open('lianjia.csv', mode='a', encoding='utf-8', newline='') as f:
            csv_write = csv.writer(f)
            csv_write.writerow([title, address, houseInfo, followInfo, tags, totalPrice, unitePrice, title_url])
