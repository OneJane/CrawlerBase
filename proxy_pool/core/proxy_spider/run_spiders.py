# 打猴子补丁
from gevent import monkey
monkey.patch_all()
# 导入协程池
from gevent.pool import Pool
import importlib
import schedule
import time

from settings import PROXIES_SPIDERS
from core.proxy_validate.httpbin_validator import check_proxy
from core.db.mongo_pool import MongoPool
from utils.log import logger
from settings import RUN_SPIDERS_INTERVAL

"""
8.5 实现运行爬虫模块
目标: 根据配置文件信息, 加载爬虫, 抓取代理IP, 进行校验, 如果可用, 写入到数据库中
思路:

1. 在run_spider.py中, 创建RunSpider类
2. 提供一个运行爬虫的run方法, 作为运行爬虫的入口, 实现核心的处理逻辑
    2.1 根据配置文件信息, 获取爬虫对象列表.
    2.2 遍历爬虫对象列表, 获取爬虫对象, 遍历爬虫对象的get_proxies方法, 获取代理IP
    2.3 检测代理IP(代理IP检测模块)
    2.4 如果可用,写入数据库(数据库模块)
    2.5 处理异常, 防止一个爬虫内部出错了, 影响其他的爬虫.
3. 使用异步来执行每一个爬虫任务, 以提高抓取代理IP效率
    3.1 在init方法中创建协程池对象
    3.2 把处理一个代理爬虫的代码抽到一个方法
    3.3 使用异步执行这个方法
    3.4 调用协程的join方法, 让当前线程等待 协程 任务的完成.
4. 使用schedule模块, 实现每隔一定的时间, 执行一次爬取任务
    4.1 定义一个start的类方法
    4.2 创建当前类的对象, 调用run方法
    4.3 使用schedule模块, 每隔一定的时间, 执行当前对象的run方法
"""

class RunSpider(object):

    def __init__(self):
        # 创建MongoPool对象
        self.mongo_pool = MongoPool()
        # 3.1 在init方法中创建协程池对象
        self.coroutine_pool = Pool()

    def get_spider_from_settings(self):
        """根据配置文件信息, 获取爬虫对象列表."""
        # 遍历配置文件中爬虫信息, 获取每个爬虫全类名
        for full_class_name in PROXIES_SPIDERS:
            # core.proxy_spider.proxy_spiders.Ip66Spider
            # 获取模块名 和 类名
            module_name, class_name = full_class_name.rsplit('.', maxsplit=1)
            # 根据模块名, 导入模块
            module = importlib.import_module(module_name)
            # 根据类名, 从模块中, 获取类
            cls = getattr(module, class_name)
            # 创建爬虫对象
            spider = cls()
            # print(spider)
            yield spider


    def run(self):
        # 2.1 根据配置文件信息, 获取爬虫对象列表.
        spiders = self.get_spider_from_settings()
        # 2.2 遍历爬虫对象列表, 获取爬虫对象, 遍历爬虫对象的get_proxies方法, 获取代理IP
        for spider in spiders:
            #  2.5 处理异常, 防止一个爬虫内部出错了, 影响其他的爬虫.
            # 3.3 使用异步执行这个方法
            # self.__execute_one_spider_task(spider)
            self.coroutine_pool.apply_async(self.__execute_one_spider_task,args=(spider, ))

        # 3.4 调用协程的join方法, 让当前线程等待 协程 任务的完成.
        self.coroutine_pool.join()

    def __execute_one_spider_task(self, spider):
        # 3.2 把处理一个代理爬虫的代码抽到一个方法
        # 用于处理一个爬虫任务的.
        try:
            # 遍历爬虫对象的get_proxies方法, 获取代理I
            for proxy in spider.get_proxies():
                # print(proxy)
                # 2.3 检测代理IP(代理IP检测模块)
                proxy = check_proxy(proxy)
                # 2.4 如果可用,写入数据库(数据库模块)
                # 如果speed不为-1, 就说明可用
                if proxy.speed != -1:
                    # 写入数据库(数据库模块)
                    self.mongo_pool.insert_one(proxy)
        except Exception as ex:
            logger.exception(ex)

    @classmethod
    def start(cls):
        # 4. 使用schedule模块, 实现每隔一定的时间, 执行一次爬取任务
        # 4.1 定义一个start的类方法
        # 4.2 创建当前类的对象, 调用run方法
        rs = RunSpider()
        rs.run()
        # 4.3 使用schedule模块, 每隔一定的时间, 执行当前对象的run方法
        # 4.3.1 修改配置文件, 增加爬虫运行时间间隔的配置, 单位为小时
        schedule.every(RUN_SPIDERS_INTERVAL).hours.do(rs.run)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    # rs = RunSpider()
    # rs.run()
    RunSpider.start()

    # 测试schedule
    # def task():
    #     print('呵呵')
    #
    # schedule.every(10).seconds.do(task)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
