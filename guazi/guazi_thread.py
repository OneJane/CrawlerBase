import re

import requests
import sys
import io
from bs4 import BeautifulSoup
import threading


# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
# 设置最大线程锁 最多10个线程同时允许
thread_lock = threading.BoundedSemaphore(value=10)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    'Cookie': 'antipas=S15242D63902f277l3069R211; uuid=054d50e6-1a28-4ab5-a511-4492c2c50905; clueSourceCode=%2A%2300; ganji_uuid=2830976934963488783473; sessionid=dcf7a42d-eb1e-419a-d030-72d398948b13; lg=1; Hm_lvt_bf3ee5b290ce731c7a4ce7a617256354=1616650869; cainfo=%7B%22ca_a%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_s%22%3A%22self%22%2C%22ca_n%22%3A%22self%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22-%22%2C%22ca_campaign%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22ca_i%22%3A%22-%22%2C%22scode%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%22054d50e6-1a28-4ab5-a511-4492c2c50905%22%2C%22ca_city%22%3A%22su%22%2C%22sessionid%22%3A%22dcf7a42d-eb1e-419a-d030-72d398948b13%22%7D; cityDomain=su; user_city_id=67; preTime=%7B%22last%22%3A1616650889%2C%22this%22%3A1616650869%2C%22pre%22%3A1616650869%7D; Hm_lpvt_bf3ee5b290ce731c7a4ce7a617256354=1616650888',
}


def getHtmlText(url):
    try:
        html = requests.get(url, headers=headers).content
        html = html.decode('utf-8')
        return html
    except:
        return '产生异常'


def get_data(html):
    # html = etree.HTML(text)
    # ul = html.xpath('//ul[@class="carlist clearfix js-top"]')[0]
    # lis = ul.xpath('./li')
    # for li in lis:
    #     detail = li.xpath('./a/@href')
    #     deatil_url = 'https:.//www.guazi.com'+deatil_url[0]
    soup = BeautifulSoup(html, 'html.parser')
    infos = soup.find('ul', {'class': 'carlist clearfix js-top'}).find_all('li')
    with open('./guazi.csv', 'a', encoding='utf-8') as f:
        pic_urls = []
        for info in infos:
            leixing = info.find('h2').get_text()
            nianfen1 = info.find('div', {'class': 't-i'}).get_text()
            nianfen2 = re.sub(r'|', '', nianfen1).split('|')
            nianfen = nianfen2[0]
            licheng = nianfen2[1]
            didian = '苏州'
            shoujia = info.find('div', {'class': 't-price'}).find('p').get_text()
            try:
                yuanjia = info.find('div', {'class': 't-price'}).find('em').get_text()
            except AttributeError:
                yuanjia = ''
            tupian = info.find('a').find('img')['src']
            pic_urls.append(tupian)
            f.write("{},{},{},{},{},{}\n".format(leixing, nianfen, licheng, didian, shoujia, yuanjia))
    return pic_urls

def download_pics(url,n):
    r = requests.get(url)
    with open(r'.\img\{}.jpg'.format(n),'wb') as f:
        f.write(r.content)
    thread_lock.release()

def main():
    n = 0
    for i in range(1,51):
        start_url = 'https://www.guazi.com/su/buy/o'+str(i)
        html = getHtmlText(start_url)
        pic_urls = get_data(html)
        for url in pic_urls:
            n+=1
            print('正在下载第{}张图片'.format(n))
            # 上锁 避免下载同一张
            thread_lock.acquire()
            t = threading.Thread(target=download_pics,args=(url,n))
            t.start()

main()
