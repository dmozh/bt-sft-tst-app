import pika

from json import dumps
from base64 import b64encode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update
from uuid import uuid4

from cache import r as cache
from logger import log
from models import KeyBody
from bus_controller import BusSenderController


class AddBodyService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, data: dict):
        key = ""
        duplicates = 0
        if isinstance(data, dict):
            for k, v in data.items():
                key += k + v
            key = b64encode(bytes(key, encoding='utf-8'))
            key = key.decode('utf-8')
            log.info(f"{key}")
            async with self.session.begin() as session:
                log.debug(f"Writing to DB")
                try:
                    select_key = select(KeyBody).where(KeyBody.requestkey == key)
                    result = await session.execute(select_key)
                    result = result.fetchone()
                    if result:
                        duplicates = result[0].duplicates + 1
                        _sql = update(KeyBody).where(KeyBody.requestkey == key).values(
                            duplicates=duplicates)
                        cache.delete(key)
                        try:
                            cache.delete('all')
                        except Exception as e:
                            log.error(f"Error when delete all from cache. Error - {e}")

                    else:
                        _sql = insert(KeyBody).values(id=str(uuid4()),
                                                      requestkey=key,
                                                      requestbody=dumps(data),
                                                      duplicates=duplicates
                                                      )
                    await session.execute(_sql)

                except Exception as e:
                    log.error(f"Error when writing run to DB. Error - {e}")
                    success = False
                    msg = f"Unhandled error when writing run. Error - {e}"
                else:
                    success = True
                    if result:
                        msg = "update"
                    else:
                        msg = "create"
        else:
            success = False
            if data:
                msg = "Incorrect type"
            else:
                msg = "No data"

        with BusSenderController() as connection:
            channel = connection.channel()
            rabbit_body = dumps({"event": "add", "key": key, "duplicates": duplicates}).encode('utf-8')
            channel.basic_publish(exchange='', routing_key='statistic_queue', body=rabbit_body)
            log.info(f" [x] Sent {rabbit_body}")
            log.info(f"Close connection")

        return dumps({"success": success, "msg": msg, "data": key})
