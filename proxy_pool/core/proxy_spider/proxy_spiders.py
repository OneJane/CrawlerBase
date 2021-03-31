import time
import random
import requests
import re
import js2py


from core.proxy_spider.base_spider import BaseSpider
from utils.http import get_request_headers

"""
1. 实现西刺代理爬虫: http://www.xicidaili.com/nn/1
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
    挂了
"""

class XiciSpider(BaseSpider):
    # 准备URL列表
    urls = ['https://www.xicidaili.com/nn/{}'.format(i) for i in range(1, 11)]
    # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="ip_list"]/tr[position()>1]'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip':'./td[2]/text()',
        'port':'./td[3]/text()',
        'area':'./td[4]/a/text()'
    }

"""
2. 实现ip3366代理爬虫: http://www.ip3366.net/free/?stype=1&page=1
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""
class Ip3366Spider(BaseSpider):
    # 准备URL列表
    urls = ['http://www.ip3366.net/free/?stype={}&page={}'.format(i, j) for i in range(1, 4, 2) for j in range(1, 8)]
    # # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip':'./td[1]/text()',
        'port':'./td[2]/text()',
        'area':'./td[5]/text()'
    }

"""
3. 实现快代理爬虫: https://www.kuaidaili.com/free/inha/1/
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""
class KaiSpider(BaseSpider):
    # 准备URL列表
    urls = ['https://www.kuaidaili.com/free/inha/{}/'.format(i) for i in range(1, 6)]
    # # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip':'./td[1]/text()',
        'port':'./td[2]/text()',
        'area':'./td[5]/text()'
    }

    # 当我们两个页面访问时间间隔太短了, 就报错了; 这是一种反爬手段.
    def get_page_from_url(self, url):
        # 随机等待1,3s
        time.sleep(random.uniform(1, 3))
        # 调用父类的方法, 发送请求, 获取响应数据
        return super().get_page_from_url(url)

"""
4. 实现proxylistplus代理爬虫: https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
"""

class ProxylistplusSpider(BaseSpider):
    # 准备URL列表
    urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'.format(i) for i in range(1, 7)]
    # # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="page"]/table[2]/tbody/tr[position()>2]'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip':'./td[2]/text()',
        'port':'./td[3]/text()',
        'area':'./td[5]/text()'
    }

"""
5. 实现66ip爬虫: http://www.66ip.cn/1.html
    定义一个类,继承通用爬虫类(BasicSpider)
    提供urls, group_xpath 和 detail_xpath
    由于66ip网页进行js + cookie反爬, 需要重写父类的get_page_from_url方法
"""

class Ip66Spider(BaseSpider):
    # 准备URL列表
    urls = ['http://www.66ip.cn/{}.html'.format(i) for i in range(1, 11)]
    # # 分组的XPATH, 用于获取包含代理IP信息的标签列表
    group_xpath = '//*[@id="main"]/div/div[1]/table/tbody/tr[position()>1]'
    # 组内的XPATH, 用于提取 ip, port, area
    detail_xpath = {
        'ip':'./td[1]/text()',
        'port':'./td[2]/text()',
        'area':'./td[3]/text()'
    }

    # 重写方法, 解决反爬问题
    def get_page_from_url(self, url):
        headers = get_request_headers()
        response = requests.get(url, headers=headers)
        if response.status_code == 521:
            # 生成cookie信息, 再携带cookie发送请求
            # 生成 `_ydclearance` cookie信息,控制台preserve log,第一个页面就是加密页面521用来做反爬跳转
            # 1. 确定 _ydclearance 是从哪里来的;
            # 观察发现: 这个cookie在前两个页面都没有返回，说明信息不使用通过服务器响应设置过来的; 那么他就是通过js生成.
            # 2. 第一次发送请求的页面中, 有一个生成这个cookie的js; 执行这段js, 生成我们需要的cookie
            # 这段js是经过加密处理后的js, 真正js在 "po" 中.
            # 提取 `jp(107)` 调用函数的方法, 以及函数
            result = re.findall('window.onload=setTimeout\("(.+?)", 200\);\s*(.+?)\s*</script> ', response.content.decode('GBK'))
            # print(result)
            # 我希望执行js时候, 返回真正要执行的js
            # 把 `eval("qo=eval;qo(po);")` 替换为 return po
            func_str = result[0][1]
            func_str = func_str.replace('eval("qo=eval;qo(po);")', 'return po')
            # print(func_str)
            # 获取执行js的环境
            context = js2py.EvalJs()
            # 加载(执行) func_str
            context.execute(func_str)
            # 执行这个方法, 生成我们需要的js
            # code = gv(50)
            context.execute('code = {};'.format(result[0][0]))
            # 打印最终生成的代码
            # print(context.code)
            cookie_str = re.findall("document.cookie='(.+?); ", context.code)[0]
            # print(cookie_str)
            headers['Cookie'] = cookie_str
            response = requests.get(url, headers=headers)
            return response.content.decode('GBK')
        else:
            return response.content.decode('GBK')


if __name__ == '__main__':
    # spider = XiciSpider()
    # spider = Ip3366Spider()
    # spider = KaiSpider()
    # spider = ProxylistplusSpider()

    # spider = Ip66Spider()
    # for proxy in spider.get_proxies():
    #     print(proxy)
    #
    # # print(Ip3366Spider.urls)
    #
    # # # 测试: http://www.66ip.cn/1.html
    # url = 'http://www.66ip.cn/1.html'
    # headers = {
    # # 必须需要Cookie，判断哪个Cookie是真正生效的->_ydclearance
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    #     # 'Cookie': '_ydclearance=35fd4248c8889feb58597e27-a31e-4f84-9edc-f1a22c16a949-1546164684;'
    # }
    # response = requests.get(url, headers=headers)
    # print(response.status_code)
    # text = response.content.decode('GBK')
    text = 'window.onload=setTimeout("jp(107)", 200); function jp(WI){var qo, mo="",no="",oo=[0xff,0x94,0x9e,0x5c,0x04,0x0f,0xce,0x86,0x47,0xfd,0x8d,0×0e,0Xcb,0x8d,0×4f,0×40,0xf5,0xb9,00x8c,0x06,0×97,0×4b,0X02,0×88,0×46,0×05,0XCC,0×88,0xba,0x67,0X23,0xe3,0xa1,0xfe,0xb6,0×26,0Xe2,0x5d,0x34,0X00,0x6d,0x24,0X9f,0x4b,0xb2,0X2f,0x98,0×56,0Xb1,0X2C,0x9e,0x5a,0XCC,0×7d,0xe4,0Xa1,0x1d,0x8f,0×16,0xdd,0×41,0xb4,0X2f,0x060xc1,0x38,0xb7,0x74,0x65,0X2c,0xe8,0x5f,0xde,0x8c,0xf2,0x69,0Xd3,0x4d,0xdf,0x5f,0X1b,0xd2,0x4d,0x76,0Xec,0x6C,0X20ea,0x3f,0xa5,0x19,0x90,0×4e,0x24,0x9d,0×05,0×77,0Xef,0x96,0×10,0×78,0Xf7,0x63,0Xea,0×52,0Xc8,0x31,0Xac,0x52,0Xca,0x34,0xa1,0x1e,0xaa,0×14,0x89,0X04,0xcb,0X7f,0x22,0xdc,0xa0,0×4d,0x34,0xfb,0xa9,0x19,0Xa6,0x15,0XCC,0x8d,0Xc,0x86,0×09,0×76,0Xf0,0x70,0×07,0×4b,0x03,0Xd0,0×50,0Xb,0×18,0×8a,0×05,0x80,0Xea,0xbb,0X30,0x97,0×0f,0x73,0xe3,0X60,0xc9,0×44,0xed,0Xd1,0x71,0×08,0x7d,0Xf7,0x35,0Xfb,0xbd,0×7d,0×39,0Xf0,0xa4,0×65,0xd4,0x55,0xf7,0x70,0Xd8,0x9c,0X47,0x290Xa9,0×67,0x28,0×9d,0Xe2,0x6d,0x18,0Xd3,0x8a,0x07,0xc9,0X390xba,0x34,xb2,0X28,0xa2,0x5c,20,0X84,0×45,0x0c,Xcd,0×77,0x2d,0Xad,0x64,0×26,0xe3,0Xf2,0xaa,0×6a,0x22,0xe2,0x8e,0x35,0xb5,0×74,0×36,0xeb,0Xa9,0x65,0×1c,0xdf,0×79,0x3b0xfb,0x6b,022,0×32,0xf3,0xb1,0×69,0x29,0Xa7,0×6f,0x30,0xd6,0x57,0×f4,0x8c,0x19,0X6a,0X3b];qo = "qo=234; do{oo[qo]=(-oo[qo])&0xff; oo[qo] = ( ((oo[qo]»2) | ((oo [qo]«6)&0xff) )-107)&0xff;} while(—qo>=2);"; eval(qo);qo = 233; do {oo[qo] = (oolqo] - oo[qo - 1]) & 0xff; } while (— qo >= 3 );qo = 1; for (;;) { if (qo > 233) break; oo[qo] =(<((((oo[qo] + 172) & 0xff) + 188) & 0xff) « 3) & 0xff) | (((((oo[qo] + 172) & 0xff) + 188) & 0xff) » 5); qo++;}po; for (qo =1; qo < oo.length - 1; qo++) if (qo % 6) po += String.fromCharCode(oo[qo] ~ XL);eval("qo=eval;qo(po);");}</script></body></html>'
    # 生成 `_ydclearance` cookie信息
    # 1. 确定 _ydclearance 是从哪里来的; 页面跳转点击Preserve log查看历史请求。请求了两次1.html,都没有_ydclearance的cookie
    # 观察发现: 这个cookie信息不使用通过服务器响应设置过来的; 那么他就是通过js生成.
    # 2. 第一次发送请求的页面中521, 有一个生成这个cookie的js; 执行这段js, 生成我们需要的cookie
    # 这段js是经过加密处理后的js, 真正js在 "po" 中.
    # 提取 `jp(107)` 调用函数方法, 以及函数内容 function jp(WI) { var qo, mo="" ...
    result = re.findall('window.onload=setTimeout\("(.+?)", 200\);\s*(.+?)\s*</script>' ,text)
    # print(result)
    # 我希望执行js时候, 返回真正要执行的js就是po
    # 把 `eval("qo=eval;qo(po);")` 替换为 return po
    func_str = result[0][1]
    func_str = func_str.replace('eval("qo=eval;qo(po);")', 'return po')
    # print(func_str)
    # # 获取执行js的环境
    # context = js2py.EvalJs()
    # # 加载(执行) func_str
    # context.execute(func_str)
    # # 执行这个方法, 生成我们需要的js
    # # code = gv(50)
    # context.execute('code = {};'.format(result[0][0]))
    # # 打印最终生成的代码
    # # print(context.code)
    # cookie_str = re.findall("document.cookie='(.+?); ", context.code)[0]
    # # print(cookie_str)
    # headers['Cookie'] = cookie_str
    # response = requests.get(url, headers=headers)
    # print(response.content.decode('GBK'))










