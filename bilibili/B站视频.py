import requests
import re


bv_id = input('请输入你想要爬取的视频ID: ')
url = f'https://www.ibilibili.com/video/{bv_id}'
headers = {
    'pragma': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',

}

response = requests.get(url=url, headers=headers, verify=False)
aid = re.findall('"aid":"(\d+)"', response.text)[0]
b_cid = re.findall('"bcid":"(\d+)"', response.text)[0]
sign = re.findall('"absign":"(.*?)"', response.text)[0]
title = re.findall('<h4>(.*?)</h4>', response.text)[0]


index_url = 'https://bilibili.applinzi.com/index.php'
data = {
    'aid': aid,
    'bcid': b_cid,
    'absign': sign,
}
headers_1 = {
    'Host': 'bilibili.applinzi.com',
    'Origin': 'https://www.ibilibili.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
}
response_1 = requests.post(url=index_url, data=data, headers=headers_1)

video_url = response_1.json()['url']
print(video_url)
headers_2 = {
    'referer': video_url,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
}
video_content = requests.get(url=video_url, headers=headers_2).content

with open(title + '.mp4', mode='wb') as f:
    f.write(video_content)