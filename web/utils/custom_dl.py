from pyrogram import raw
from pyrogram import Client
from pyrogram import types


class TGCustomYield:

    def __init__(self, client: Client):
        self.client = client

    async def generate_file_properties(self, media_msg: types.Message):
        pass

    async def generate_media_session(self, client: Client, media_msg: types.Message):
        pass

    async def get_location(self, data):
        pass

    async def download_as_bytesio(self, media_msg: types.Message):
        client = self.client
        data = await self.generate_file_properties(media_msg)
        media_session = await self.generate_media_session(client, media_msg)

        location = await self.get_location(data)

        limit = 1024 * 1024
        offset = 0

        r = await media_session.send(
            raw.functions.upload.GetFile(
                location=location,
                offset=offset,
                limit=limit
            )
        )

        if isinstance(r, raw.types.upload.File):
            m_file = []
            while True:
                chunk = r.bytes

                if not chunk:
                    break

                m_file.append(chunk)

                offset += limit

                r = await media_session.send(
                    raw.functions.upload.GetFile(
                        location=location,
                        offset=offset,
                        limit=limit
                    )
                )

            return m_file
            
