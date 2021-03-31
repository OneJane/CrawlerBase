from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
from queue import Queue
import schedule
import time

from core.db.mongo_pool import MongoPool
from core.proxy_validate.httpbin_validator import check_proxy
from settings import MAX_SCORE, TEST_PROXIES_ASYNC_COUNT, TEST_PROXIES_INTERVAL

"""
9. 实现代理池的检测模块
目的: 检查代理IP可用性, 保证代理池中代理IP基本可用
思路
    1. 在proxy_test.py中, 创建ProxyTester类
    2. 提供一个 run 方法, 用于处理检测代理IP核心逻辑
        2.1 从数据库中获取所有代理IP
        2.2 遍历代理IP列表
        2.3 检查代理可用性
        2.4 如果代理不可用, 让代理分数-1, 如果代理分数等于0就从数据库中删除该代理, 否则更新该代理IP
        2.5 如果代理可用, 就恢复该代理的分数, 更新到数据库中
    3. 为了提高检查的速度, 使用异步来执行检测任务
        3.1 在`init`方法, 创建队列和协程池
        3.2 把要检测的代理IP, 放到队列中
        3.3 把检查一个代理可用性的代码, 抽取到一个方法中; 从队列中获取代理IP, 进行检查; 检查完毕, 调度队列的task_done方法
        3.4 通过异步回调, 使用死循环不断执行这个方法,
        3.5 开启多个一个异步任务, 来处理代理IP的检测; 可以通过配置文件指定异步数量
   4. 使用schedule模块, 每隔一定的时间, 执行一次检测任务
        4.1 定义类方法 start, 用于启动检测模块
        4.2 在start方法中
            4.2.1 创建本类对象
            4.2.2 调用run方法
            4.2.3 每间隔一定时间, 执行一下, run方法  
"""

class ProxyTester(object):

    def __init__(self):
        # 创建操作数据库的MongoPool对象
        self.mongo_pool = MongoPool()
        # 3.1 在`init`方法, 创建队列和协程池
        self.queue = Queue()
        self.coroutine_pool = Pool()

    def __check_callback(self, temp):
        self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

    def run(self):
        # 提供一个 run 方法, 用于处理检测代理IP核心逻辑
        # 2.1 从数据库中获取所有代理IP
        proxies = self.mongo_pool.find_all()
        # 2.2 遍历代理IP列表
        for proxy in proxies:
            #  3.2 把要检测的代理IP, 放到队列中
            self.queue.put(proxy)

        #  3.5 开启多个一个异步任务, 来处理代理IP的检测; 可以通过配置文件指定异步数量
        for i in range(TEST_PROXIES_ASYNC_COUNT):
            #  3.4 通过异步回调, 使用死循环不断执行这个方法,
            self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

        # 让当前线程, 等待队列任务完成
        self.queue.join()

    def __check_one_proxy(self):
        # 检查一个代理IP的可用性
        #  3.3 把检查一个代理可用性的代码, 抽取到一个方法中;
        # 从队列中获取代理IP, 进行检查; 检查完毕
        proxy = self.queue.get()
        #  2.3 检查代理可用性
        proxy = check_proxy(proxy)
        # 2.4 如果代理不可用, 让代理分数-1,
        if proxy.speed == -1:
            proxy.score -= 1
            # 如果代理分数等于0就从数据库中删除该代理
            if proxy.score == 0:
                self.mongo_pool.delete_one(proxy)
            else:
                # 否则更新该代理IP
                self.mongo_pool.update_one(proxy)
        else:
            # 2.5 如果代理可用, 就恢复该代理的分数, 更新到数据库中
            proxy.score = MAX_SCORE
            self.mongo_pool.update_one(proxy)
        # 调度队列的task_done方法
        self.queue.task_done()

    @classmethod
    def start(cls):
        #  4.2.1 创建本类对象
        proxy_tester = cls()
        #  4.2.2 调用run方法
        proxy_tester.run()

        # 4.2.3 每间隔一定时间, 执行一下, run方法
        schedule.every(TEST_PROXIES_INTERVAL).hours.do(proxy_tester.run)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    # pt = ProxyTester()
    # pt.run()
    ProxyTester.start()

