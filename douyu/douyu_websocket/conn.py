import json
import asyncio
from typing import Optional, Any
from urllib.parse import urlparse
from abc import ABC, abstractmethod

from aiohttp import ClientSession, WSMsgType, ClientError


class Conn(ABC):
    """
    定义连接抽象基类
    """
    __slots__ = ('_url', '_receive_timeout',)

    # receive_timeout 推荐为 heartbeat 间隔加 10s 或 5s
    @abstractmethod
    def __init__(self, url: str, receive_timeout: Optional[float] = None):
        self._url = url
        self._receive_timeout = receive_timeout

    @abstractmethod
    async def open(self) -> bool:
        return False

    @abstractmethod
    async def close(self) -> bool:
        return True
        
    # 用于永久 close 之后一些数据清理等
    @abstractmethod
    async def clean(self) -> None:
        pass

    @abstractmethod
    async def send_bytes(self, bytes_data: bytes) -> bool:
        return True

    @abstractmethod
    async def read_bytes(self) -> Optional[bytes]:
        return None

    @abstractmethod
    async def read_json(self) -> Any:
        return None

    # 类似于 https://docs.python.org/3/library/asyncio-stream.html#asyncio.StreamReader.readexactly
    # Read exactly n bytes.
    @abstractmethod
    async def read_exactly_bytes(self, n: int) -> Optional[bytes]:
        return None

    # 类似于 https://docs.python.org/3/library/asyncio-stream.html#asyncio.StreamReader.readexactly
    # Read exactly n bytes.
    @abstractmethod
    async def read_exactly_json(self, n: int) -> Any:
        return None


class WsConn(Conn):
    """
    继承连接抽象基类WebSocket连接
    """
    __slots__ = ('_is_sharing_session', '_session', '_ws_receive_timeout', '_ws_heartbeat', '_ws')

    # url 格式 ws://hostname:port/… 或者 wss://hostname:port/…
    def __init__(
            self, url: str,
            receive_timeout: Optional[float] = None,
            session: Optional[ClientSession] = None,
            ws_receive_timeout: Optional[float] = None,  # 自动 ping pong 时候用的
            ws_heartbeat: Optional[float] = None):  # 自动 ping pong 时候用的
        super().__init__(url, receive_timeout)
        result = urlparse(url)
        if result.scheme != 'ws' and result.scheme != 'wss':
            raise TypeError(f'url scheme must be websocket ({result.scheme})')
        self._url = url

        # 创建session
        if session is None:
            self._is_sharing_session = False
            self._session = ClientSession()
        else:
            self._is_sharing_session = True
            self._session = session
        self._ws_receive_timeout = ws_receive_timeout
        self._ws_heartbeat = ws_heartbeat
        self._ws = None

    async def open(self) -> bool:
        try:
            # 等待连接websocket
            self._ws = await asyncio.wait_for(
                self._session.ws_connect(
                    self._url,
                    receive_timeout=self._ws_receive_timeout,
                    heartbeat=self._ws_heartbeat), timeout=3)
        except (ClientError, asyncio.TimeoutError):
            return False
        return True
        
    async def close(self) -> bool:
        if self._ws is not None:
            await self._ws.close()
        return True
        
    async def clean(self) -> None:
        if not self._is_sharing_session:
            await self._session.close()
        
    async def send_bytes(self, bytes_data: bytes) -> bool:
        try:
            await self._ws.send_bytes(bytes_data)
        except ClientError:
            return False
        except asyncio.CancelledError:
            return False
        return True
                
    async def read_bytes(self) -> Optional[bytes]:
        try:
            msg = await asyncio.wait_for(
                self._ws.receive(), timeout=self._receive_timeout)
            if msg.type == WSMsgType.BINARY:
                return msg.data
        except (ClientError, asyncio.TimeoutError):
            return None
        except asyncio.CancelledError:
            # print('asyncio.CancelledError', 'read_bytes')
            return None
        return None

    async def read_json(self) -> Any:
        try:
            msg = await asyncio.wait_for(
                self._ws.receive(), timeout=self._receive_timeout)
            if msg.type == WSMsgType.TEXT:
                return json.loads(msg.data)
            elif msg.type == WSMsgType.BINARY:
                return json.loads(msg.data.decode('utf8'))
        except (ClientError, asyncio.TimeoutError):
            return None
        except asyncio.CancelledError:
            # print('asyncio.CancelledError', 'read_json')
            return None
        return None

    async def read_exactly_bytes(self, n: int) -> Optional[bytes]:
        raise NotImplementedError("Sorry, but I don't think we need this in WebSocket.")

    async def read_exactly_json(self, n: int) -> Any:
        raise NotImplementedError("Sorry, but I don't think we need this in WebSocket.")
