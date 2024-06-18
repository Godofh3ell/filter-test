import math
import logging
import secrets
import mimetypes
from urllib.parse import quote_plus
from aiohttp import web
from info import BIN_CHANNEL
from utils import temp
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from web.utils.render_template import media_watch

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text='<h1 align="center"><a href="https://t.me/SL_Bots_Updates"><b>SL Bots</b></a></h1>', content_type='text/html')

@routes.get("/watch/{message_id}")
async def watch_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return web.Response(text=await media_watch(message_id), content_type='text/html')
    except Exception as e:
        logging.exception(f"Error in watch_handler: {e}")
        return web.Response(text="<h1>Something went wrong</h1>", content_type='text/html')

@routes.get("/download/{message_id}")
async def download_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return await media_download(request, message_id)
    except Exception as e:
        logging.exception(f"Error in download_handler: {e}")
        return web.Response(text="<h1>Something went wrong</h1>", content_type='text/html')

async def media_download(request, message_id: int):
    try:
        range_header = request.headers.get('Range', None)
        media_msg = await temp.BOT.get_messages(BIN_CHANNEL, [message_id])
        file_properties = await TGCustomYield(temp.BOT).generate_file_properties(media_msg)
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
        body = TGCustomYield(temp.BOT).yield_file(media_msg, offset, first_part_cut, last_part_cut, part_count, new_chunk_size)

        file_name = file_properties.file_name if file_properties.file_name else f"{secrets.token_hex(2)}.jpeg"
        mime_type = file_properties.mime_type if file_properties.mime_type else mimetypes.guess_type(file_name)[0]

        return_resp = web.Response(
            status=206 if range_header else 200,
            body=body,
            headers={
                "Content-Type": mime_type,
                "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
                "Content-Disposition": f'attachment; filename="{quote_plus(file_name)}"',
                "Accept-Ranges": "bytes",
            }
        )

        if return_resp.status == 200:
            return_resp.headers.add("Content-Length", str(file_size))

        return return_resp

    except Exception as e:
        logging.exception(f"Error in media_download: {e}")
        return web.Response(text="<h1>Download failed</h1>", content_type='text/html')

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app)
