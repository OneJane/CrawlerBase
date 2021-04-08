import asyncio

from douyu.douyu_websocket.ws_douyu_danmu_client import WsDanmuClient

room_id = 4921614 # 22222 # 312212
area_id = 0


async def danmu_client(client):
    """
    创建任务的方式
    ensure_future: 最高层的函数，推荐使用！
    create_task: 在确定参数是 coroutine 的情况下可以使用。
    Task: 可能很多时候也可以工作，但真的没有使用的理由！
    @param client:
    @return:
    """
    connection = client(room_id, area_id)
    asyncio.ensure_future(connection.run_forever())  # run_forever 会一直运行，直到 stop 被调用
    await asyncio.sleep(2000)
    await connection.reset_roomid(room_id)
    print('RESTED')
    connection.pause()
    await asyncio.sleep(200)
    print('resume')
    connection.resume()
    await asyncio.sleep(20)
    print('close')
    await connection.close()
    print('END')


async def ws_danmu_client():
    await danmu_client(WsDanmuClient)

if __name__ == '__main__':

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ws_danmu_client())  # run_until_complete 来运行 loop ，等到 future 完成，run_until_complete 也就返回了
    loop.close()
