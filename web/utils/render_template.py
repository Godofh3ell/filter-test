# filter-test/web/utils/render_template.py

from aiohttp import web
from web.utils.custom_dl import TGCustomYield
from info import DOWNLOAD_PASSWORD  # Assuming DOWNLOAD_PASSWORD is imported from info.py

async def media_watch(request):
    # Placeholder implementation for media watch
    return web.Response(text="Media Watch Content", content_type='text/html')

async def download_file(request):
    message_id = request.match_info.get('message_id')
    if not message_id:
        return web.Response(status=400, text="Message ID is required")

    # Check for password protection
    password = request.query.get('password')
    if password != DOWNLOAD_PASSWORD:
        return web.Response(status=403, text="Unauthorized: Invalid password")

    # Generate and return the download response
    async with TGCustomYield() as tg_custom_yield:
        file_data = await tg_custom_yield.get_file(message_id)
        if not file_data:
            return web.Response(status=404, text="File not found")

        return web.Response(body=file_data, content_type='application/octet-stream')
