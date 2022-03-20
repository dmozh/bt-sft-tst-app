from json import dumps
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from cache import r as cache
from logger import log
from models import KeyBody
from bus_controller import BusSenderController


class DeleteBodyService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def delete(self, key):
        async with self.session.begin() as session:
            log.debug(f"Deleting from DB for key {key}")
            try:
                delete_from_keybody = delete(KeyBody)
                delete_from_keybody = delete_from_keybody.where(KeyBody.requestkey == key)
                await session.execute(delete_from_keybody)

            except Exception as e:
                msg = f"Error when delete on {key} from DB. Error - {e}"
                log.error(msg)
                success = False
            else:
                success = True
                msg = "deleted"
                try:
                    cache.delete(key)
                except Exception as e:
                    log.error(f"Error when delete from cache for key {key}. Error - {e}")
        try:
            cache.delete('all')
        except Exception as e:
            log.error(f"Error when delete from cache. Error - {e}")

        with BusSenderController() as connection:
            channel = connection.channel()
            rabbit_body = dumps({"event": "delete", "key": key}).encode('utf-8')
            channel.basic_publish(exchange='', routing_key='statistic_queue', body=rabbit_body)
            log.info(f" [x] Sent {rabbit_body}")
            log.info(f"Close connection")

        return dumps({"msg": msg, "success": success, "data": key})
