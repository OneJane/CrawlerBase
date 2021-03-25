from pprint import pprint

import requests

# (.*?): (.*)  替换为 "$1":"$2", http 客户端发送请求，服务端设置cookie, 获取最开始cookie, 删除所有cookie后刷新逐个尝试Set-Cookie
api_url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
headers = {
    "origin": "https://www.lagou.com",
    "referer": "https://www.lagou.com/jobs/list_C%2B%2B/p-city_0?&cl=false&fromSearch=true&labelWords=&suginput=",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "cookie": "JSESSIONID=ABAAAECABFAACEA5949F03800B2E61BE8CB6A193C5688F8; WEBTJ-ID=20210325%E4%B8%8B%E5%8D%8810:54:43225443-17869e16744371-0312d611c6b1c2-5771031-2073600-17869e16745a34; RECOMMEND_TIP=true; PRE_UTM=; PRE_HOST=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; user_trace_token=20210325225446-b2253638-7c43-45bc-97f8-6bda895a7317; LGSID=20210325225446-3800acc6-ac0b-4fae-9f01-25930b4396d0; PRE_SITE=https%3A%2F%2Fwww.lagou.com; LGUID=20210325225446-ab6ad361-376b-4b7d-a4b5-4ab7cc11b76b; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1616684083; _ga=GA1.2.1776870788.1616684084; _gat=1; sajssdk_2015_cross_new_user=1; sensorsdata2015session=%7B%7D; _gid=GA1.2.2118996955.1616684084; index_location_city=%E6%B1%9F%E8%8B%8F; TG-TRACK-CODE=index_navigation; __lg_stoken__=453e22d2251af051f544d23c9192a91333a9d43821b322d0011d603229c2e79cbf002ee8dca46f2a0c3511d24cb54e730fa5594f3dd3a4eaf5b999bcb8c418ff421f38a1cdfa; X_HTTP_TOKEN=5c49b1c1817271606814866161427816972187273b; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2217869e1695d69d-0bbe415eb3af9c-5771031-2073600-17869e1695ea77%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24os%22%3A%22Windows%22%2C%22%24browser%22%3A%22Chrome%22%2C%22%24browser_version%22%3A%2289.0.4389.90%22%7D%2C%22%24device_id%22%3A%2217869e1695d69d-0bbe415eb3af9c-5771031-2073600-17869e1695ea77%22%7D; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1616684184; LGRID=20210325225626-2ba68b2d-9158-4274-9c59-e9c63f3f1747; SEARCH_ID=61dea7a6f4904095ac5dc6a69c8646b5"
}
data = {
    "first": "true",
    "pn": "1",
    "kd": "C++"
}
resp = requests.post(api_url, headers=headers)
pprint(resp.json())
data = resp.json()
result = data['content']['positionResult']['result']
# [print(r) for r in result]
for r in result:
    d = {
        'city': r['city'],
        'companyFullName': r['companyFullName'],
        'companySize': r['companySize'],
        'education': r['education'],
        'positionName': r['positionName'],
        'salary': r['salary'],
        'workYear': r['workYear']
    }
    with open('拉钩职位.csv',mode='a',encoding='utf-8') as f:
        f.write(",".join(d.values()))
        f.write("\n")


