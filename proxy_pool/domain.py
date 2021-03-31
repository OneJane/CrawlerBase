from settings import MAX_SCORE

"""
4. 定义代理IP的数据模型类
目标: 定义代理IP的数据模型类
步骤:

1. 定义Proxy类, 继承object
2. 实现__init__方法, 负责初始化, 包含如下字段:
    ip: 代理的IP地址
    port: 代理IP的端口号
    protocol: 代理IP支持的协议类型,http是0, https是1, https和http都支持是2
    nick_type: 代理IP的匿名程度, 高匿:0, 匿名: 1, 透明:2
    speed: 代理IP的响应速度, 单位s
    area: 代理IP所在地区
    score: 代理IP的评分, 用于衡量代理的可用性; 默认分值可以通过配置文件进行配置. 在进行代理可用性检查的时候, 每遇到一次请求失败就减1份, 减到0的时候从池中删除. 如果检查代理可用, 就恢复默认分值
    disable_domains: 不可用域名列表, 有些代理IP在某些域名下不可用, 但是在其他域名下可用
    在配置文件: settings.py 中 定义MAX_SCORE = 50, 表示代理IP的默认最高分数
3. 提供 __str__ 方法, 返回数据字符串
"""

class Proxy(object):

    def __init__(self, ip, port, protocol=-1, nick_type=-1, speed=-1, area=None, score=MAX_SCORE, disable_domains=[]):
        # ip: 代理的IP地址
        self.ip = ip
        # port: 代理IP的端口号
        self.port = port
        # protocol: 代理IP支持的协议类型, http是0, https是1, https和http都支持是2，-1不可用
        self.protocol = protocol
        # nick_type: 代理IP的匿名程度, 高匿: 0, 匿名: 1, 透明: 2
        self.nick_type = nick_type
        # speed: 代理IP的响应速度, 单位s
        self.speed = speed
        # area: 代理IP所在地区
        self.area = area
        # score: 代理IP的评分, 用于衡量代理的可用性;
        self.score = score
        # 默认分值可以通过配置文件进行配置.在进行代理可用性检查的时候, 每遇到一次请求失败就减1份, 减到0的时候从池中删除.如果检查代理可用, 就恢复默认分值
        # disable_domains: 不可用域名列表, 有些代理IP在某些域名下不可用, 但是在其他域名下可用
        self.disable_domains = disable_domains

    # 3. 提供 __str__ 方法, 返回数据字符串
    def __str__(self):
        # 返回数据字符串
        return str(self.__dict__)