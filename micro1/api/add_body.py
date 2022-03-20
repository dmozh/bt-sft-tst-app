from abc import ABC

from json import loads
from tornado.web import RequestHandler

from database import controller

from service.add_body import AddBodyService


class AddBodyHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

    async def post(self):
        data = self.request.body.decode(encoding='utf-8')
        sessionmaker = next(controller.get_session())
        svc = AddBodyService(session=sessionmaker)
        result = await svc.add(loads(data))
        self.write(result)
