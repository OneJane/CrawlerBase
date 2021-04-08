from enum import IntEnum
from struct import Struct
from typing import Tuple, Iterator


class Header:
    message_size = 4  # 数据包长度4字节小端整数
    body_header_message_size = 4   # 数据包头数据包长度4字节小端整数
    type_size = 2  # 消息类型2字节小端整数 689 690
    encrypt_size = 1  # 加密字段1字节小端整数
    other_size = 1  # 保留字段1字节小端整数

    # header_struct.size == raw_header_size
    """
    二进制数据处理
    <表示字节顺序是小端整数，也是网络序
    2个I | unsigned int | integer,
    1个H | unsigned short | integer, 
    2个B | unsigned char | Integer
    """
    header_struct = Struct('<2I1H2B')
    raw_header_size = message_size + body_header_message_size + type_size + encrypt_size + other_size

    @staticmethod
    def pack(message_size: int, body_header_message_size: int, type_size: int, encrypt_size: int, other_size: int) -> bytes:
        return Header.header_struct.pack(message_size, body_header_message_size, type_size, encrypt_size, other_size)

    @staticmethod
    def unpack(header: bytes) -> Tuple[int, int, int, int, int]:
        message_size, body_header_message_size, type_size, encrypt_size, other_size = Header.header_struct.unpack_from(header)
        if not encrypt_size and not other_size:
            return message_size,body_header_message_size, type_size, encrypt_size, other_size
        raise ValueError('encrypt != 0 || other != 0')


class Pack:
    # 打包
    @staticmethod
    def pack(str_body: str, pack_type: int, encrypt: int = 0, other: int = 0) -> bytes:
        body = str_body.encode('utf-8')
        # 数据部分以\0结尾
        end = b'\x00'
        message_size = Header.body_header_message_size + Header.type_size + Header.encrypt_size + Header.other_size + len(body) + len(end)
        header = Header.pack(message_size, message_size, pack_type, encrypt, other)
        return header + body + end

    # 解包
    @staticmethod
    def unpack(packs: bytes) -> Iterator[Tuple[int, bytes]]:
        pack = 0
        len_packs = len(packs)
        while pack != len_packs:
            message_size, body_header_message_size, type_size, encrypt_size, other_size = Header.unpack(packs[pack:pack+Header.raw_header_size])
            next_pack = pack + message_size + Header.message_size
            body = packs[pack+Header.raw_header_size:next_pack - 1]  # 因为最后一个字节是无效0
            yield type_size, body
            pack = next_pack


class PackType:
    # 客户端发送给弹幕服务器的文本格式数据
    SEND = 689
    # 弹幕服务器发送给客户端的文本格式数据
    REPLY = 690
