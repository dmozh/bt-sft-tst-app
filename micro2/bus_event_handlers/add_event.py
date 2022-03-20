from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update
from uuid import uuid4

from cache import r as cache
from logger import log
from models import Duplicates


class AddEventHandler:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, data: dict):
        key = data['key']
        duplicates = data['duplicates']
        if isinstance(data, dict):
            log.info(f"{key}")
            async with self.session.begin() as session:
                log.debug(f"Writing to DB duplicates")
                try:
                    select_key = select(Duplicates).where(Duplicates.requestkey == key)
                    result = await session.execute(select_key)
                    result = result.fetchone()
                    if result:
                        _sql = update(Duplicates).where(Duplicates.requestkey == key).values(
                            duplicates=duplicates)
                    else:
                        _sql = insert(Duplicates).values(id=str(uuid4()),
                                                         requestkey=key,
                                                         duplicates=duplicates
                                                         )
                    await session.execute(_sql)

                except Exception as e:
                    log.error(f"Error when writing run to DB. Error - {e}")
                    success = False
                    msg = f"Unhandled error when writing run. Error - {e}"
        try:
            cache.delete('statistic')
        except Exception as e:
            log.error(f"Error when delete from cache. Error - {e}")
        # return dumps({"success": success, "msg": msg, "data": key})
