import time
import math
import logging
import secrets
import mimetypes
from aiohttp import web
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from web.utils.render_template import media_watch
from urllib.parse import quote_plus
from info import DOWNLOAD_PASSWORD  # Import the DOWNLOAD_PASSWORD variable

routes = web.RouteTableDef()

@routes.get("/download/{message_id}")
async def download_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        password = request.query.get('password', '')  # Extract password from query parameters
        if password != DOWNLOAD_PASSWORD:
            return web.Response(text="<h1>Unauthorized</h1>", status=401, content_type='text/html')

        return await media_download(request, message_id)
    except Exception as e:
        logging.error(f"Error during download: {e}")
        return web.Response(text="<h1>Something went wrong</h1>", content_type='text/html')

async def media_download(request, message_id: int):
    try:
        range_header = request.headers.get('Range', 0)
        media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
        file_properties = await TGCustomYield().generate_file_properties(media_msg)
        file_size = file_properties.file_size

        if range_header:
            from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
            from_bytes = int(from_bytes)
            until_bytes = int(until_bytes) if until_bytes else file_size - 1
        else:
            from_bytes = request.http_range.start or 0
            until_bytes = request.http_range.stop or file_size - 1

        req_length = until_bytes - from_bytes

        new_chunk_size = await chunk_size(req_length)
        offset = await offset_fix(from_bytes, new_chunk_size)
        first_part_cut = from_bytes - offset
        last_part_cut = (until_bytes % new_chunk_size) + 1
        part_count = math.ceil(req_length / new_chunk_size)
        body = TGCustomYield().yield_file(media_msg, offset, first_part_cut, last_part_cut, part_count,
