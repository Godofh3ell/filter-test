from aiohttp import web
import urllib.parse
import aiofiles
from web.utils.render_template import media_watch

async def handle_request(request):
    message_id = request.query.get('message_id')
    provided_password = request.query.get('password')
    html_content = await media_watch(message_id, provided_password)
    return web.Response(text=html_content, content_type='text/html')

app = web.Application()
app.router.add_get('/media', handle_request)

if __name__ == '__main__':
    web.run_app(app, port=8080)
  
