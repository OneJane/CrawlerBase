import requests
from lxml import etree

url="http://www.xbiquge.la/10/10489/"

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}

# 会返回一个response对象，这个对象里存在的是服务器返回的所有信息，包括响应头 状态码等等
# 其中返回的网页部分会存在.content和.text两个对象中。
# 返回的是一堆乱码这时用.content.decode('utf-8')就可以使其显示正常。
res=requests.get(url,headers=headers).content.decode('utf-8')


#把HTML文档转为xml文档 方便使用xpath语法查找元素节点
book_xml=etree.HTML(res)

# 使用xpath语法查找数据 一种路径语法
# //div[@id="info"]/h1/text() 众多div里面我只想要那个id为info的对不对 那此时怎么办 我们可以通过过滤去拿到
# *表通配符 可以匹配任何元素节点（必须要有唯一id）//跳过任意层级 []过滤语法 @选取属性用的（属性就是标签里面的）
book_name=book_xml.xpath('//div[@id="info"]/h1/text()')[0]#书籍名称
print(book_name)
book_title=book_xml.xpath("//div[@id='list']/dl/dd/a/text()") #书籍标题
# print(book_title)
book_url=book_xml.xpath("//div[@id='list']/dl/dd/a/@href")  #章节链接 一堆url(所有章节)
# print(book_url)
print("书籍名称：《{}》".format(book_name))

# 开文件流   打开一个文件 把我们数据写入到文件中去    a是追加写入 写入完第一章就继续追加写入第二章
with open(book_name + '.txt', 'a', encoding='utf-8')as f:
    f.write(book_name+'\n')

    # title 章节的名称     urls 每个章节的详情链接
    # 遍历获取到该本书的每个章节和对应的内容详情链接  zip一次性遍历多个列表
    for title,urls in zip(book_title,book_url):

        print(urls)
        # 可能后台网站开发只给出这么多东西  那自动拼接上主机名 这样才是一个完整的网址
        c_url='http://www.xbiquge.la'+urls

        print(title)
        print(c_url)

        # 异常处理
        try: #捕捉异常
            #参数1：单个章节的url:以获取到这个章节的小说内容的html源码 参数2：headers  参数3：请求等待时间3秒
            titles_url = requests.get(c_url, headers=headers, timeout=3).content.decode('utf-8')
        except: # 如果捕捉异常怎么办  请求失败那就再请求一遍
            titles_url = requests.get(c_url, headers=headers).content.decode('utf-8')

        # 那我们还差一个小说文本内容对不对 那每个章节链接我们有了
        # 每个章节里面的内容是不是好解决 一样xpath语法给他获取下来
        # 通过xpath获取到小说文本内容
        book_content = etree.HTML(titles_url).xpath('//*[@id="content"]/text()')

        f.write(title) # 先写入章节名称
        f.write('\n')

        # f.write不能够写列表，但可以写字符串格式（二进制）。。。  所以要for循环
        for line in book_content:
            f.write(line) # 再写入章节对应的内容
        f.write('\n')  # 每写完一章换行  一共1000多个章节



