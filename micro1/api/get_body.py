from abc import ABC

from tornado.web import RequestHandler
from logger import log
from database import controller

from service.get_body import GetBodyService, get_cache



class GetBodyHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

    async def get(self):
        try:
            key = self.request.arguments['key'][0].decode(encoding='utf-8')
        except KeyError:
            key = None
        cache = get_cache(key)
        if cache:
            log.info(f"Return from cache")
            self.write(cache)
        else:
            sessionmaker = next(controller.get_session())
            svc = GetBodyService(session=sessionmaker)
            result = await svc.get(key)
            self.write(result)
