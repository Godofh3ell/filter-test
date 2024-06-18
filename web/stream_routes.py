import aiofiles
import math
import os
import secrets
from aiohttp import web
from urllib.parse import quote_plus
from utils import temp
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from web.utils.render_template import media_watch, download_file
from info import BIN_CHANNEL, PASSWORD, URL

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text='<h1 align="center"><a href="https://t.me/SL_Bots_Updates"><b>SL Bots</b></a></h1>', content_type='text/html')

@routes.get("/watch/{message_id}")
async def watch_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return web.Response(text=await media_watch(message_id), content_type='text/html')
    except:
        return web.Response(text="<h1>Something went wrong</h1>", content_type='text/html')

@routes.get("/download/{message_id}")
async def download_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return await download_file(request, message_id)
    except:
        return web.Response(text="<h1>Something went wrong</h1>", content_type='text/html')
