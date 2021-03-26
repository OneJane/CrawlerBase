import requests
import os



# 1、提取所有英雄编号
url='https://pvp.qq.com/web201605/js/herolist.json'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                  '87.0.4280.88 Safari/537.36'
}

# 发送请求--requests 模拟浏览器发送请求，获取响应数据  前后端数据传递的一种数据格式
herolist=requests.get(url,headers=headers).json()
# print(herolist)


#那我们遍历上面这个列表就能拿到每个英雄的字典数据
for i in herolist:
    # 所有英雄编号   所有英雄名称   每个英雄的皮肤数量
    print(i['ename'],i['cname'],i['hero_type'])
    for a in range(i['hero_type']):
        a+=1   #要把总数量分别提取出来变成1 2 3
        print(a)
        img='http://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{}/{}-bigskin-{}.jpg'.format(i['ename'],i['ename'],a)
        print(img)
        hero_img_data=requests.get(img).content
        # 'img/英雄名字/皮肤图片'
        if not os.path.exists('img/%s'%i['cname']):
            os.mkdir('img/%s'%i['cname'])
        # 英雄名字  英雄皮肤的编号
        with open('img/%s/%s.jpg'%(i['cname'],a),'wb') as f:
            f.write(hero_img_data)