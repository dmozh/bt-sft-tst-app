from abc import ABC

from json import dumps, loads
from json.decoder import JSONDecodeError
from tornado.web import RequestHandler

from database import controller


from service.upd_body import UpdateBodyService
from utils import handle_parse
from logger import log

class UpdateBodyHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

    async def put(self, key):
        if key:
            data = self.request.body.decode(encoding='utf-8')
            try:
                d_data = loads(data)
            except JSONDecodeError as e:
                log.error(e)
                d_data = handle_parse(data)
            sessionmaker = next(controller.get_session())
            svc = UpdateBodyService(session=sessionmaker)
            result = await svc.update(key, d_data)
            self.write(result)
        else:
            self.write(dumps({'msg': "not found"}))
