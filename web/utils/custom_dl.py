# web/utils/custom_dl.py

import math
from typing import Union
from pyrogram.types import Message
from pyrogram import Client, raw
from pyrogram.session import Session, Auth
from pyrogram.errors import AuthBytesInvalid, RPCError
from pyrogram.file_id import FileId, FileType

class TGCustomYield:
    def __init__(self, bot: Client):
        self.main_bot = bot

    async def generate_file_properties(self, msg: Message) -> FileId:
        try:
            if msg.video:
                media = msg.video
            elif msg.document:
                media = msg.document
            else:
                raise ValueError("Message does not contain video or document")

            file_id_obj = FileId.decode(media.file_id)
            file_id_obj.file_size = media.file_size
            file_id_obj.mime_type = media.mime_type
            file_id_obj.file_name = media.file_name

            return file_id_obj
        except Exception as e:
            raise ValueError(f"Error while generating file properties: {e}") from e

    async def generate_media_session(self, client: Client, msg: Message) -> Session:
        try:
            data = await self.generate_file_properties(msg)
            media_session = client.media_sessions.get(data.dc_id, None)

            if media_session is None:
                if data.dc_id != await client.storage.dc_id():
                    media_session = Session(
                        client, data.dc_id, await Auth(client, data.dc_id, await client.storage.test_mode()).create(),
                        await client.storage.test_mode(), is_media=True
                    )
                    await media_session.start()

                    for _ in range(3):
                        exported_auth = await client.invoke(
                            raw.functions.auth.ExportAuthorization(
                                dc_id=data.dc_id
                            )
                        )

                        try:
                            await media_session.send(
                                raw.functions.auth.ImportAuthorization(
                                    id=exported_auth.id,
                                    bytes=exported_auth.bytes
                                )
                            )
                        except AuthBytesInvalid:
                            continue
                        else:
                            break
                    else:
                        await media_session.stop()
                        raise AuthBytesInvalid
                else:
                    media_session = Session(
                        client, data.dc_id, await client.storage.auth_key(),
                        await client.storage.test_mode(), is_media=True
                    )
                    await media_session.start()

                client.media_sessions[data.dc_id] = media_session

            return media_session
        except Exception as e:
            raise RuntimeError(f"Error while generating media session: {e}") from e

    async def get_location(self, file_id: FileId) -> Union[raw.types.InputVideoFileLocation, raw.types.InputDocumentFileLocation]:
        try:
            if file_id.file_type == FileType.VIDEO:
                location = raw.types.InputVideoFileLocation(
                    id=file_id.media_id,
                    access_hash=file_id.access_hash,
                    file_reference=file_id.file_reference,
                    thumb_size=file_id.thumbnail_size
                )
            elif file_id.file_type == FileType.DOCUMENT:
                location = raw.types.InputDocumentFileLocation(
                    id=file_id.media_id,
                    access_hash=file_id.access_hash,
                    file_reference=file_id.file_reference,
                    thumb_size=file_id.thumbnail_size
                )
            else:
                raise ValueError(f"Unsupported file type: {file_id.file_type}")

            return location
        except Exception as e:
            raise ValueError(f"Error while getting file location: {e}") from e

    async def yield_file(self, media_msg: Message, offset: int, first_part_cut: int,
                         last_part_cut: int, part_count: int, chunk_size: int) -> Union[str, None]:
        try:
            client = self.main_bot
            data = await self.generate_file_properties(media_msg)
            media_session = await self.generate_media_session(client, media_msg)

            current_part = 1

            location = await self.get_location(data)

            r = await media_session.send(
                raw.functions.upload.GetFile(
                    location=location,
                    offset=offset,
                    limit=chunk_size
                ),
            )

            if isinstance(r, raw.types.upload.File):
                while current_part <= part_count:
                    chunk = r.bytes
                    if not chunk:
                        break
                    offset += chunk_size
                    if part_count == 1:
                        yield chunk[first_part_cut:last_part_cut]
                        break
                    if current_part == 1:
                        yield chunk[first_part_cut:]
                    if 1 < current_part <= part_count:
                        yield chunk

                    r = await media_session.send(
                        raw.functions.upload.GetFile(
                            location=location,
                            offset=offset,
                            limit=chunk_size
                        ),
                    )

                    current_part += 1
        except RPCError as e:
            raise RuntimeError(f"RPCError: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Error while yielding file: {e}") from e

    async def download_as_bytesio(self, media_msg: Message) -> Union[list, None]:
        try:
            client = self.main_bot
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
        except RPCError as e:
            raise RuntimeError(f"RPCError: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Error while downloading as bytesio: {e}") from e
