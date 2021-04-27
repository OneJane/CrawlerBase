import execjs
from gevent.pool import Pool

from redis import StrictRedis
import random
import requests
import regex as re
import js2py
import pickle

from dishonest.dishonest.settings import REDIS_URL, USER_AGENTS
from dishonest.dishonest.settings import COOKIES_KEY, COOKIES_PROXY_KEY, COOKIES_USER_AGENT_KEY, REDIS_COOKIES_KEY
"""
实现生成cookie的脚本

1. 创建gen_gsxt_cookies.py文件, 在其中创建GenGsxtCookie的类
2. 实现一个方法, 用于把一套代理IP, User-Agent, Cookie绑定在一起的信息放到Redis的list中
    随机获取一个User-Agent
    随机获取一个代理IP
    获取request的session对象
    把User-Agent, 通过请求头, 设置给session对象
    把代理IP, 通过proxies, 设置给session对象
    使用session对象, 发送请求, 获取需要的cookie信息
    把代理IP, User-Agent, Cookie放到字典中, 序列化后, 存储到Redis的list中
3. 实现一个run方法, 用于开启多个异步来执行这个方法.

注: 为了和下载器中间件交互方便, 需要再settings.py中配置一些常量.
"""

class GenGsxtCookie(object):

    def __init__(self):
        """建立Redis数据库连接"""
        self.redis = StrictRedis.from_url(REDIS_URL)
        # 创建协程池对象
        self.pool = Pool()

    def push_cookie_to_redis(self):

        while True:
            try:
                """
                2. 实现一个方法, 用于把一套代理IP, User-Agent, Cookie绑定在一起的信息放到Redis的list中
                """
                # 1. 随机获取一个User-Agent
                user_agent = random.choice(USER_AGENTS)
                # 2. 随机获取一个代理IP
                # response = requests.get('http://localhost:16888/random?protocol=http')
                # proxy = response.content.decode()
                # 3. 获取requests的session对象
                session = requests.session()
                # 4. 把User-Agent, 通过请求头, 设置给session对象
                session.headers = {
                    'User-Agent': user_agent
                }
                # 5. 把代理IP, 通过proxies, 设置给session对象
                # session.proxies = {
                #     'http': proxy
                # }
                # 6. 使用session对象, 发送请求, 获取需要的cookie信息
                index_url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-xxgg-100000.html'
                # 获取request的session对象, 可以自动合并cookie信息

                # ######################################################使用session发送index_url请求###########################
                response = session.get(index_url)
                print(response.status_code)
                # 第一次请求521 服务器借助这个请求设置一个Set-Cookie: __jsluid_h=8af7a39f7cdb1c46f8f624c972968c8f; max-age=31536000; path=/; HttpOnly到本地，并返回一段js
                ########################################################拿到第一个cookie########################
                # 1. 提取script标签中的js
                js1 = re.findall('<script>(.+?)</script>', response.content.decode())[0].replace('document.cookie=',
                                                                                                 '').replace(
                    'location.href=location.pathname+location.search', '')
                context = js2py.EvalJs()
                ###################################################根据第一个请求返回的js生成第二个cookie###############################
                context.execute('cookies2 =' + js1)
                cookies = context.cookies2.split(';')[0].split('=')
                session.cookies.set(cookies[0], cookies[1])  # 到此拿到第两个cookie
                ######################################################拿到第二个cookie############################

                # 第二次请求携带Cookie: __jsluid_h=6ed2648e0a734bc66e3011d648f6f1ab; __jsl_clearance=1619152879.013|-1|aS3lFknWlGtD%2FADiygf7vxl4yqk%3D返回一段js
                # 添加jsdom实现浏览器上下文
                js2 = '''const jsdom = require("jsdom");const {JSDOM} = jsdom;const dom = new JSDOM();window = dom.window;document = window.document;location = new Array();''' + \
                      re.findall('<script>(.+?)</script>', session.get(index_url).content.decode('utf-8'))[0]
                # 正则获取document['cookie']，由于每次个数不一样我们取最后一个
                cookies2_1 = re.findall(r"document\[.*?\]=(.*?)location", js2, re.S)[-1]
                # 将document['cookie']内容返回给go函数
                js3 = re.sub("};go", "return " + cookies2_1 + "};go", js2, 1)
                # 获取调用go函数时里面的参数
                request = re.findall(r"go\({(.*?)}\)", js3, re.S)[-1]
                # 通过python修改js生成一个request方法
                final_js = js3 + "\nfunction request() {return go({" + request + "})}"
                # js调用request方法返回cookie并将新的__jsl_clearance塞给session中
                cookies3 = execjs.compile(final_js).call('request').split(';')[0].split('=')
                session.cookies.set(cookies3[0], cookies3[1])

                # 第三次请求 修改了__jsl_clearance后服务端向客户端设置新cookie的SECTOKEN
                session.get(index_url)
                cookies = requests.utils.dict_from_cookiejar(session.cookies)
                # print(cookies)
                # 7. 把代理IP, User-Agent, Cookie放到字典中, 序列化后, 存储到Redis的list中
                cookies_dict = {
                    COOKIES_KEY:cookies,
                    COOKIES_USER_AGENT_KEY:user_agent,
                    # COOKIES_PROXY_KEY:proxy
                }
                # 序列化后, 存储到Redis的list中
                self.redis.lpush(REDIS_COOKIES_KEY, pickle.dumps(cookies_dict))
                print(cookies_dict)
                break
            except Exception as ex:
                print("error",ex)

    def run(self):
        # 清空之前的cookie信息
        self.redis.delete(REDIS_COOKIES_KEY)
        # 3. 实现一个run方法, 用于开启多个异步来执行这个方法.
        for i in range(3):
            self.pool.apply_async(self.push_cookie_to_redis)
        # # 让主线程等待所有的, 协程任务完成
        self.pool.join()

if __name__ == '__main__':
    ggc = GenGsxtCookie()
    ggc.run()