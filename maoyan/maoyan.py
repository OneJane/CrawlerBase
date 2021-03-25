import requests
import parsel
import csv

url = 'https://maoyan.com/board'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'Host': 'maoyan.com',
    'Cookie': 'uuid_n_v=v1; uuid=7DAFD070084211EBB74D8BF51EFE42AF124E2687E17044E581A302EF3F38BDF7; _csrf=9220c1be47a862d8bacf4b6b3d890a971430da88fcb23edf58734760f46b0786; _lxsdk_cuid=17500d437f5c8-0340068bf87d32-333376b-1fa400-17500d437f5c8; _lxsdk=7DAFD070084211EBB74D8BF51EFE42AF124E2687E17044E581A302EF3F38BDF7; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1602036709; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1602036744; __mta=141849229.1602036709488.1602036735481.1602036744302.5; _lxsdk_s=17500d437f6-29-bc0-c4c%7C%7C17'
}
response = requests.get(url=url, headers=headers)
response.encoding = response.apparent_encoding
html_data = response.text
print(html_data, response.headers)
selector = parsel.Selector(html_data)
print(selector)
dds = selector.css('.board-wrapper dd')
for dd in dds:
    title = dd.css('.name a::attr(title)').get()
    star = dd.css('.star::text').get().strip()
    releasetime = dd.css('.releasetime::text').get()
    score = dd.css('.score i::text').getall()
    score = ''.join(score)
    print(title, star, releasetime, score)

    with open('maoyan.csv', mode='a', encoding='utf-8', newline='') as f:
        csv_write = csv.writer(f)
        csv_write.writerow([title, star, releasetime, score])
