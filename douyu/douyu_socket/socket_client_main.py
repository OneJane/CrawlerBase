#!/usr/bin/python3
# -*- coding: utf-8 -*-

import asyncore
import sys


# 1. 定义类并且继承自 asyncore.dispatcher
class SocketClient(asyncore.dispatcher):
    # 2. 实现类中的回调函数代码
    def __init__(self, host, port):
        # 调用父类方法
        asyncore.dispatcher.__init__(self)

        # 创建 Socket 对象
        self.create_socket()

        # 连接服务器
        address = (host, port)
        self.connect(address)
        pass

    # 实现 handle_connect 回调函数
    def handle_connect(self):
        print("连接成功")

    # 实现 writable 回调函数
    def writable(self):
        return False

    # 实现 handle_write 回调函数
    def handle_write(self):
        # 调用 send 方法对服务器发送数据，参数是字节数据
        self.send('hello world\n'.encode('utf-8'))

    # 实现 readable 回调函数
    def readable(self):
        return True

    # 实现 handle_read 回调函数
    def handle_read(self):
        # 主动接收数据，参数是需要接收数据的长度
        result = self.recv(1024)
        print(result)

    # 实现 handle_error 回调函数
    def handle_error(self):
        # 编写处理错误方法
        t, e, trace = sys.exc_info()
        self.close()

    # 实现 handle_close 回调函数
    def handle_close(self):
        print("连接关闭")
        self.close()




if __name__ == '__main__':
    # netcat-win32-1.12>nc -l -p 9000  启动服务端

    client = SocketClient('127.0.0.1', 9000)
    # 3.创建对象并且执行 asyncore.loop 进入运行循环
    asyncore.loop(timeout=5)
