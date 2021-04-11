import time

import parsel
import requests

for page in range(1,3466):
    print('==============正在爬去第{}页数据==================='.format(page))
    base_url = 'https://www.doutula.com/photo/list/?page={}'.format(page)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
    response = requests.get(url=base_url,headers=headers)
    html_data=response.text

    selector = parsel.Selector(html_data)
    result_list = selector.xpath('//a[@class="col-xs-6 col-sm-3"]')
    for result in result_list:
        img_url = result.xpath('./img/@data-original').extract_first()
        img_title = result.xpath('./img/@alt').extract_first()
        if img_title.strip() == '' or img_title is None:
            img_title = int(time.time())
        all_title = str(img_title)+'.'+img_url.split('.')[-1]

        img_data = requests.get(url=img_url,headers=headers).content
        with open('img\\'+all_title,mode='wb') as f:
            print('保存完成',all_title)
            f.write(img_data)