import logging
import time
import os
import platform
from pyrogram import Client, __version__, types
from aiohttp import web
from database.ia_filterdb import Media
from database.users_chats_db import db
from web.utils.render_template import media_watch, download_file
from info import PASSWORD, LOG_CHANNEL, API_ID, API_HASH, BOT_TOKEN, PORT, BIN_CHANNEL
from utils import temp
from typing import Optional, AsyncGenerator, Union

# Handle request for media watch
async def handle_request(request):
    message_id = request.query.get('message_id')
    if message_id is None:
        return web.Response(status=400, text="message_id is required")
    try:
        message_id = int(message_id)
    except ValueError:
        return web.Response(status=400, text="Invalid message_id")
    
    html_content = await media_watch(message_id)
    return web.Response(text=html_content, content_type='text/html')

# Handle request for file download with password protection
async def handle_download(request):
    response = await download_file(request)
    return response

class Bot(Client):
    def __init__(self):
        super().__init__(
            name='Auto_Filter_Bot',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"}
        )
        self.web_app = web.Application()
        self.web_app.router.add_get('/media', handle_request)
        self.web_app.router.add_get('/download/{message_id}', handle_download)
        self.runner = web.AppRunner(self.web_app)

    async def start(self):
        temp.START_TIME = time.time()
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()

        if os.path.exists('restart.txt'):
            with open("restart.txt") as file:
                chat_id, msg_id = map(int, file.read().split())
            try:
                await self.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
            except Exception as e:
                print(f"Error editing message text: {e}")
            os.remove('restart.txt')

        temp.BOT = self
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        username = '@' + me.username

        await self.runner.setup()
        site = web.TCPSite(self.runner, "0.0.0.0", PORT)
        await site.start()

        try:
            await self.send_message(chat_id=LOG_CHANNEL, text=f"<b>{me.mention} Restarted! 🤖</b>")
        except Exception as e:
            print(f"Error sending message to LOG_CHANNEL: {e}")
            exit()

        try:
            m = await self.send_message(chat_id=BIN_CHANNEL, text="Test")
            await m.delete()
        except Exception as e:
            print(f"Error sending message to BIN_CHANNEL: {e}")
            exit()

        print(f"\nPyrogram [v{__version__}] Bot [{username}] Started With Python [v{platform.python_version()}]\n")

    async def stop(self, *args):
        await super().stop()
        await self.runner.cleanup()
        print("Bot Stopped! Bye...")

    async def iter_messages(self: Client, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator[types.Message, None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff)))
            for message in messages:
                yield message
                current += 1

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    bot = Bot()
    bot.run()
