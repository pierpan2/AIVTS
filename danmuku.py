# -*- coding: utf-8 -*-
import asyncio
import http.cookies
from typing import *

import aiohttp

import blivedm
import blivedm.models.web as web_models


# 这里填一个已登录账号的cookie的SESSDATA字段的值。不填也可以连接，但是收到弹幕的用户名会打码，UID会变成0
# SESSDATA = ''

session: Optional[aiohttp.ClientSession] = None


async def listen(room_id, cookie, stop_event, callback):
    init_session(cookie)
    try:
        await run_single_client(room_id, stop_event, callback)
    finally:
        await session.close()


def init_session(cookie):
    cookies = http.cookies.SimpleCookie()
    cookies['SESSDATA'] = cookie
    cookies['SESSDATA']['domain'] = 'bilibili.com'

    global session
    session = aiohttp.ClientSession()
    session.cookie_jar.update_cookies(cookies)


async def run_single_client(room_id, stop_event, callback):
    """
    演示监听一个直播间
    """

    # Get room id
    room_id = room_id
    client = blivedm.BLiveClient(room_id, session=session)
    handler = MyHandler(callback)
    client.set_handler(handler)

    client.start()
    try:
        
        await stop_event.wait()
        client.stop()

        await client.join()
    finally:
        await client.stop_and_close()


class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    def __init__(self, callback):
        self.callback = callback

    def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
        print(f'[{client.room_id}] 心跳')
        self.callback('心跳')

    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname}：{message.msg}')
        self.callback(message)

    def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')
        self.callback(message)

    def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')
        self.callback(message)

    def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')
        self.callback(message)

