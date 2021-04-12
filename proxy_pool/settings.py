
# 在配置文件: settings.py 中 定义MAX_SCORE = 50, 表示代理IP的默认最高分数
MAX_SCORE = 50

# 日志的配置信息
import logging
# 默认的配置
LOG_LEVEL = logging.DEBUG    # 默认等级
LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'   # 默认日志格式
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
LOG_FILENAME = 'log.log'    # 默认日志文件名称

# 测试代理IP的超时时间
TEST_TIMEOUT = 10

# MongoDB数据库的URL
MONGO_URL = 'mongodb://127.0.0.1:27017'


PROXIES_SPIDERS = [
    # 爬虫的全类名,路径: 模块.类名
    'core.proxy_spider.proxy_spiders.Ip66Spider',
    'core.proxy_spider.proxy_spiders.Ip3366Spider',
    'core.proxy_spider.proxy_spiders.KaiSpider',
    'core.proxy_spider.proxy_spiders.ProxylistplusSpider',
    # 'core.proxy_spider.proxy_spiders.XiciSpider',
]

# 4.3.1 修改配置文件, 增加爬虫运行时间间隔的配置, 单位为小时
RUN_SPIDERS_INTERVAL = 2
# 配置检测代理IP的异步数量
TEST_PROXIES_ASYNC_COUNT = 10
# 配置检查代理IP的时间间隔, 单位是小时
TEST_PROXIES_INTERVAL = 2

# 配置获取的代理IP最大数量; 这个越小可用性就越高; 但是随机性越差
PROXIES_MAX_COUNT = 50