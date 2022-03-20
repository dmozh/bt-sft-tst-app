from logger import log
from models import Duplicates
from json import dumps, loads
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from cache import r as cache


def get_cache(key):
    _key = key
    if _key is None:
        _key = 'all'
    log.info(f"Try get from cache for key {_key}")
    return cache.get(_key)


class GetBodyService:
    def __init__(self, session):
        self.session = session

    async def statistics(self, key):
        body = ""
        async with self.session.begin() as session:
            log.debug(f"Selecting from DB")
            try:
                select_from_duplicates = select(Duplicates)
                if key:
                    select_from_duplicates_on_key = select_from_duplicates.where(Duplicates.requestkey == key)
                    _ = await session.execute(select_from_duplicates_on_key)
                    _ = _.fetchall()
                    key_duplicates = int(_[0][0].duplicates)

                    _ = await session.execute(select_from_duplicates)
                    _ = _.fetchall()
                    all_duplicates = 0
                    for item in _:
                        all_duplicates += int(item[0].duplicates)
                    all_reqs_count = all_duplicates+len(_)
                    try:
                        result = key_duplicates/all_reqs_count
                    except ZeroDivisionError:
                        result = 0
                else:
                    _ = await session.execute(select_from_duplicates)
                    _ = _.fetchall()
                    all_duplicates = 0
                    for item in _:
                        all_duplicates += int(item[0].duplicates)
                    all_reqs_count = all_duplicates + len(_)
                    try:
                        result = (all_duplicates / all_reqs_count)*100
                    except ZeroDivisionError:
                        result = 0
                log.info(f"{str(round(result, 2))}")
            except Exception as e:
                log.error(f"Error when selecting run to DB. Error - {e}")
                msg = f"Unhandled error when selecting run. Error - {e}"
                success = False
            else:
                success = True
                if result is not None:
                    body = {"duplicates": f"{round(result, 4)}%"}
                    msg = "success"
                else:
                    success = False
                    msg = "Not found"
        expire = 60
        response = dumps({"success": success, "msg": msg, "data": body})
        # TODO add cache
        if key:
            cache.set(key, response)
            cache.expire(key, ttl=expire)
        return response
