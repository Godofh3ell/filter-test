import logging
from aiohttp import web
from web.utils.render_template import media_watch, download_file

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text='<h1 align="center"><a href="https://t.me/SL_Bots_Updates"><b>SL Bots</b></a></h1>', content_type='text/html')

@routes.get("/media_watch/{message_id}")
async def watch_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return await media_watch(request)
    except Exception as e:
        logging.error(f"Error in watch handler: {e}")
        return web.Response(text="<h1>Something went wrong</h1>", content_type='text/html')

@routes.get("/download/{message_id}")
async def download_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return await download_file(request)
    except Exception as e:
        logging.error(f"Error in download handler: {e}")
        return web.Response(text="<h1>Something went wrong</h1>", content_type='text/html')

async def media_watch(message_id):
    # Implement your logic for media watching here
    pass

async def chunk_size(req_length):
    # Implement your logic for chunk size calculation here
    pass

async def offset_fix(from_bytes, new_chunk_size):
    # Implement your logic for offset fixing here
    pass

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app)
    
