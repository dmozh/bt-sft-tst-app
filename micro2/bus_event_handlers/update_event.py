from json import dumps
from base64 import b64encode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from uuid import uuid4

from cache import r as cache
from logger import log
from models import Duplicates


class UpdateEventHandler:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, data: dict):
        new_key = data['new_key']
        old_key = data['key']

        async with self.session.begin() as session:
            log.debug(f"Writing to DB")
            try:
                _sql = update(Duplicates).where(Duplicates.requestkey == old_key) \
                    .values(requestkey=new_key,
                            duplicates=0)
                await session.execute(_sql)
                try:
                    cache.delete('statistic')
                    cache.delete(old_key)
                except Exception as e:
                    log.error(f"Error when delete all from cache. Error - {e}")
            except Exception as e:
                log.error(f"Error when update run to DB. Error - {e}")
                success = False
                msg = f"Unhandled error when update run. Error - {e}"
            else:
                success = True
                msg = "success"
