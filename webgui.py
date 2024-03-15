import asyncio
from nicegui import ui

from danmuku import listen
import blivedm.models.web as web_models

stop_event = asyncio.Event()

def handle_comment(comment_text):
    # if isinstance(comment_text, web_models.DanmakuMessage):
    print(type(comment_text).__name__+'\naaa\n')
    

async def call_listen(room_id, cookie):
    global stop_event
    stop_event.set()
    await asyncio.sleep(2)
    stop_event = asyncio.Event()
    await listen(room_id, cookie, stop_event, handle_comment)

with ui.row():
    room_id = ui.input('直播间号')
    room_id.value = '123456'
    # ui.button('Button', on_click=lambda: ui.notify(room_id.value))

with ui.row():
    cookie = ui.input('Cookie用以显示完整观众名')
    cookie.value = ''
    ui.button('连接直播间', on_click=lambda: call_listen(int(room_id.value), cookie.value))

with ui.row():
    vts_port = ui.input('Vtube Studio端口')
    vts_port.value = 8001
    ui.button('连接VTS', on_click=lambda: ui.notify(vts_port.value))

ui.run()