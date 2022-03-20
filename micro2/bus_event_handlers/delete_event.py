from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from cache import r as cache
from logger import log
from models import Duplicates


class DeleteEventHandler:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, data: dict):
        async with self.session.begin() as session:
            log.debug(f"Deleting from DB for key {data['key']}")
            try:
                _sql = delete(Duplicates)
                _sql = _sql.where(Duplicates.requestkey == data['key'])
                await session.execute(_sql)

            except Exception as e:
                msg = f"Error when delete on {data['key']} from DB. Error - {e}"
                log.error(msg)
                success = False
            else:
                success = True
                msg = "deleted"
        try:
            cache.delete('statistic')
            cache.delete(data['key'])
        except Exception as e:
            log.error(f"Error when delete from cache. Error - {e}")