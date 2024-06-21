import os
import aiofiles
import urllib.parse
from aiohttp import web
from web.utils.custom_dl import TGCustomYield
from utils import temp
from info import BIN_CHANNEL, URL, PASSWORD

async def media_watch(request):
    try:
        message_id = int(request.match_info['message_id'])
    except ValueError:
        return web.Response(text='<h1>Invalid message_id</h1>', content_type='text/html')

    media_msg = await temp.BOT.get_messages(BIN_CHANNEL, [message_id])
    if not media_msg:
        return web.Response(text='<h1>Message not found</h1>', content_type='text/html')

    try:
        file_properties = await TGCustomYield(temp.BOT).generate_file_properties(media_msg)
    except ValueError:
        return web.Response(text='<h1>File properties not found or incomplete.</h1>', content_type='text/html')

    file_name, mime_type = file_properties.file_name, file_properties.mime_type
    src = urllib.parse.urljoin(URL, f'download/{message_id}')
    tag = mime_type.split('/')[0].strip()
    if tag == 'video':
        async with aiofiles.open('web/template/watch.html') as r:
            heading = f'Watch - {file_name}'
            html = (await r.read()).replace('tag', tag) % (heading, file_name, src)
    else:
        html = '<h1>This is not a streamable file</h1>'

    return web.Response(text=html, content_type='text/html')

async def download_file(request):
    try:
        message_id = int(request.match_info['message_id'])
    except ValueError:
        return web.Response(text='<h1>Invalid message_id</h1>', content_type='text/html')

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

    media_msg = await temp.BOT.get_messages(BIN_CHANNEL, [message_id])
    if not media_msg:
        return web.Response(text='<h1>Message not found</h1>', content_type='text/html')

    try:
        file_properties = await TGCustomYield(temp.BOT).generate_file_properties(media_msg)
    except ValueError:
        return web.Response(text='<h1>File properties not found or incomplete.</h1>', content_type='text/html')

    file_name = file_properties.file_name
    file_path = f"downloads/{file_name}"

    if not os.path.exists(file_path):
        async with aiofiles.open(file_path, 'wb') as f:
            async for chunk in TGCustomYield(temp.BOT).download_as_bytesio(media_msg):
                await f.write(chunk)

    return web.FileResponse(file_path)

