import time

import parsel
import requests
from tornado import concurrent

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}


def send_request(url):
    """请求数据"""
    response = requests.get(url=url, headers=headers, verify=False)
    return response


def parse_data(data):
    """数据解析"""
    selector = parsel.Selector(data)
    result_list = selector.xpath('//a[@class="col-xs-6 col-sm-3"]')
    for result in result_list:
        title = result.xpath('./img/@alt').extract_first()
        src_url = result.xpath('./img/@data-original').extract_first()
        if title.strip() == '' or title is None:
            title = int(time.time())
        all_title = str(title) + '.' + src_url.split('.')[-1]
        yield all_title, src_url


def save_data(file_name, data):
    """数据保存"""
    with open('img\\' + file_name, mode='wb') as f:
        print('保存完成', file_name)
        f.write(data)


def main(page):
    """函数入口"""
    for page in range(1, page + 1):
        print('==============正在爬去第{}页数据==================='.format(page))
        thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        res = send_request('https://www.doutula.com/photo/list/?page={}'.format(str(page)))
        src_url = parse_data(res.text)
        for file, url in src_url:
            image_response = send_request(url)
            thread_pool.submit(save_data, file, image_response.content)
        thread_pool.shutdown()


if __name__ == '__main__':
    main(10)
