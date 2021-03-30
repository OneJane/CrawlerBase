"""

    1. 确定需求,爬取喜马拉雅音频文件数据
        对于喜马拉雅这个网站进行分析, 找到我们想要的数据来源.
            1. 找到 音频 真实的url地址  可下载url地址
            2. 找到 https://www.ximalaya.com/revision/play/v1/audio?id=45982775&ptype=1 返回json数据
                里面包含音频url地址  每一个音频ID对应一个数据包URL地址
            3. 音频ID https://www.ximalaya.com/xiangsheng/9723091/ 在我们的网页源代码中可以就获取了.
    
    
    2. 对url https://www.ximalaya.com/xiangsheng/9723091/ 地址发送请求 获取它网页源代码
    3. 解析数据 提取网页源代码中 音频ID 标题
    4. 把音频ID传入到 https://www.ximalaya.com/revision/play/v1/audio?id=45982775&ptype=1  
        获取json数据 可以解析得到 音频的url地址
    5. 请求 音频url地址 保存到本地
爬虫流程:
    请求了三个url地址:
        1. https://www.ximalaya.com/xiangsheng/9723091/ 获取音频ID
        2. https://www.ximalaya.com/revision/play/v1/audio?id=45982775&ptype=1  获取音频url地址
        3. 音频url地址 保存数据

"""
import requests  # 第三方模块 需要大家去 pip install requests
import parsel # 数据解析模块  第三方模块  pip install parsel
import pprint # 格式化输出的模块

# 发送请求
for page in range(2, 6):
    print(f'===========================现在正在爬起第{page}页数据内容=============================')
    url = f'https://www.ximalaya.com/xiangsheng/9723091/p{page}/'
    # 为什么要加请求头: 把我们python代码伪装成浏览器进行请求访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }

    response = requests.get(url=url, headers=headers)
    # response.text 获取网页一个文本数据  response.json() 获取json数据  response.content 获取二进制数据
    # print(response.text)
    # 对网页源代码进行 数据解析 提取 标题/音频ID
    selector = parsel.Selector(response.text)
    # print(response.text)
    # getall() 取多个标签 内容 返回的数据是一个列表形式保存的
    titles = selector.css('.sound-list li.lF_ a::attr(title)').getall()
    href = selector.css('.sound-list li.lF_ a::attr(href)').getall()
    # zip() 可以讲两个列表进行打包, 遍历之后 是一个元组
    data = zip(titles, href)
    for index in data:
        title = index[0]
        mp3_id = index[1].split('/')[-1]
        # f'{mp3_id}'  '{}'.format(mp3_id) 字符串格式化方法
        index_url = f'https://www.ximalaya.com/revision/play/v1/audio?id={mp3_id}&ptype=1'
        response_1 = requests.get(url=index_url, headers=headers)
        # 什么是json数据  字典嵌套字典  还嵌套一些列表
        # json数据取值和字典取值方式是一样的  根据关键词提取内容  通俗的讲 就是根据左边的内容提取右边的内容
        # print(response_1.text)
        mp3_url = response_1.json()['data']['src']
        print(title, mp3_url)
        # 保存数据
        # 保存数据: 如果是图片/音频/视频 等 都是要获取它的二进制数据,要以二进制的数据保存
        mp3_content = requests.get(url=mp3_url).content
        # 相对路径
        with open('相声\\' + title + '.mp3', mode='wb') as f:
            f.write(mp3_content)
            print('正在保存: ', title)















