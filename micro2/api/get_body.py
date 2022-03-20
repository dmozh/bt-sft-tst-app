from abc import ABC

from tornado.web import RequestHandler
from logger import log
from database import controller
from json import loads

from service.get_body import GetBodyService, get_cache


class GetBodyHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

    async def get(self):
        try:
            key = self.request.arguments['key'][0].decode(encoding='utf-8')
        except KeyError:
            key = None
        if key:
            cache = get_cache(key)
        else:
            cache = None
        if cache:
            log.info(f"Return from cache")
            self.write(cache)
        else:
            sessionmaker = next(controller.get_session())
            svc = GetBodyService(session=sessionmaker)
            result = await svc.statistics(key)
            self.write(result)
