import asyncio
from aiohttp import web
from pyrogram import Client, types
from info import DOWNLOAD_PASSWORD, BIN_CHANNEL, URL
from utils.custom_dl import TGCustomYield

async def media_watch(request):
    # Implement your media watch logic here
    pass

async def download_file(request):
    try:
        message_id = int(request.match_info['message_id'])
    except ValueError:
        return web.Response(status=400, text="Invalid message_id")

    password = request.query.get('password', '')
    if password != DOWNLOAD_PASSWORD:
        return web.Response(status=401, text="Unauthorized access")

    try:
        media_msg = await client.get_messages(BIN_CHANNEL, message_ids=message_id)
        if not media_msg.media:
            return web.Response(status=400, text="Message does not contain media")

        total_size = media_msg.file_size if media_msg.file_size else media_msg.document.file_size
        offset, first_part_cut, last_part_cut, part_count = 0, 0, 0, 0
        while offset < total_size:
            result = await TGCustomYield().get_location(media_msg, offset, total_size)
            offset, first_part_cut, last_part_cut, part_count = result[1:]
        return web.Response(
            body=TGCustomYield().yield_file(media_msg, offset, first_part_cut, last_part_cut, part_count),
            headers={'Content-Disposition': f'attachment; filename="{media_msg.file_name or "file"}"'}
        )
    except Exception as e:
        return web.Response(status=500, text=f"Internal Server Error: {str(e)}")
