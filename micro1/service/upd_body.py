from json import dumps
from base64 import b64encode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from uuid import uuid4

from cache import r as cache
from logger import log
from models import KeyBody
from bus_controller import BusSenderController


class UpdateBodyService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def update(self, key: str, data: dict):
        if key:
            new_key = ''
            if isinstance(data, dict):
                for k, v in data.items():
                    new_key += k + v
                new_key = b64encode(bytes(key, encoding='utf-8'))
                new_key = new_key.decode('utf-8')
                log.info(f"{new_key}")
                async with self.session.begin() as session:
                    log.debug(f"Writing to DB")
                    try:
                        update_into_keybody = update(KeyBody).where(KeyBody.requestkey == key) \
                            .values(requestkey=new_key,
                                    requestbody=dumps(data),
                                    duplicates=0)
                        await session.execute(update_into_keybody)
                        _ = data['duplicates'] = 0
                        cache.set(new_key, _)
                        cache.expire(new_key, 86400)
                        try:
                            cache.delete('all')
                        except Exception as e:
                            log.error(f"Error when delete all from cache. Error - {e}")
                    except Exception as e:
                        log.error(f"Error when update run to DB. Error - {e}")
                        success = False
                        msg = f"Unhandled error when update run. Error - {e}"
                    else:
                        success = True
                        msg = "success"
            else:
                success = False
                if data:
                    msg = "Incorrect type"
                else:
                    msg = "No data"

            with BusSenderController() as connection:
                channel = connection.channel()
                rabbit_body = dumps({"event": "update", "key": key, "new_key": new_key, "duplicates": 0}).encode('utf-8')
                channel.basic_publish(exchange='', routing_key='statistic_queue', body=rabbit_body)
                log.info(f" [x] Sent {rabbit_body}")
                log.info(f"Close connection")

            return dumps({"success": success, "msg": msg, "data": new_key})
        else:
            return dumps({"success": False, "msg": "No key"})