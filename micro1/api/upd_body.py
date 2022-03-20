from abc import ABC

from json import loads
from tornado.web import RequestHandler

from database import controller

from json import dumps
from service.upd_body import UpdateBodyService


class UpdateBodyHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

    async def put(self, key):
        if key:
            data = self.request.body.decode(encoding='utf-8')
            sessionmaker = next(controller.get_session())
            svc = UpdateBodyService(session=sessionmaker)
            result = await svc.update(key, loads(data))
            self.write(result)
        else:
            self.write(dumps({'msg': "not found"}))
