from json import dumps, loads
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from cache import r as cache
from logger import log
from models import KeyBody


def get_cache(key):
    _key = key
    if _key is None:
        _key = 'all'
    log.info(f"Try get from cache for key {_key}")
    return cache.get(_key)


class GetBodyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, key):
        body = ""
        duplicates = 0
        async with self.session.begin() as session:
            log.debug(f"Selecting from DB")
            try:
                select_from_keybody = select(KeyBody)
                if key:
                    select_from_keybody = select_from_keybody.where(KeyBody.requestkey == key)
                _ = await session.execute(select_from_keybody)
                _ = _.fetchall()
                result = []
                for item in _:
                    body = loads(item[0].requestbody)
                    body["duplicates"] = item[0].duplicates
                    result.append(body)
                # result = [loads(item[0].requestbody) for item in _]
                log.info(f"{result}")
            except Exception as e:
                log.error(f"Error when selecting run to DB. Error - {e}")
                msg = f"Unhandled error when selecting run. Error - {e}"
                success = False
            else:
                success = True
                if result:
                    if key:
                        body = result[0]
                    else:
                        body = {"data": result}
                    msg = "success"
                else:
                    success = False
                    msg = "Not found"
        response = dumps({"success": success, "msg": msg, "data": body})
        if key:
            cache.set(key, response)
            cache.expire(key, 86400)
        else:
            cache.set('all', response)
            cache.expire('all', 86400)
        return response
