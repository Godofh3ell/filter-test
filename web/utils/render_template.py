import os
import aiofiles
import urllib.parse
from aiohttp import web
from web.utils.custom_dl import TGCustomYield
from utils import temp
from info import BIN_CHANNEL, URL, DOWNLOAD_PASSWORD


async def media_watch(message_id):
    message_id = int(message_id)
    media_msg = await temp.BOT.get_messages(BIN_CHANNEL, [message_id])
    try:
        file_properties = await TGCustomYield(temp.BOT).generate_file_properties(media_msg)
    except ValueError:
        return web.Response(text='<h1>File type not supported or not found.</h1>', content_type='text/html')

    file_name, mime_type = file_properties.file_name, file_properties.mime_type
    src = urllib.parse.urljoin(URL, f'download/{message_id}')
    tag = mime_type.split('/')[0].strip()
    if tag == 'video':
        async with aiofiles.open('web/template/watch.html') as r:
            heading = 'Watch - {}'.format(file_name)
            html = (await r.read()).replace('tag', tag) % (heading, file_name, src)
    else:
        html = '<h1>This is not a streamable file</h1>'
    return web.Response(text=html, content_type='text/html')

async def download_handler(request, message_id):
    provided_password = request.query.get('password')

    if provided_password != PASSWORD:
        return web.Response(text='''
            <html>
                <head><title>Password Required</title></head>
                <body>
                    <h1>Enter Password to Download the File</h1>
                    <form method="get">
                        <input type="password" name="password" required />
                        <button type="submit">Submit</button>
                    </form>
                </body>
            </html>
        ''', content_type='text/html')

    try:
        message_id = int(message_id)
        return await media_download(request, message_id)
    except Exception as e:
        logging.error(f"Error during download: {e}")
        return web.Response(text="<h1>Something went wrong</h1>", content_type='text/html')

async def media_download(request, message_id):
    range_header = request.headers.get('Range', 0)
    media_msg = await temp.BOT.get_messages(BIN_CHANNEL, [message_id])
    file_properties = await TGCustomYield().generate_file_properties(media_msg)
    file_size = file_properties.file_size

    if range_header:
        from_bytes
