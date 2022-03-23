from abc import ABC

from json import loads
from json.decoder import JSONDecodeError
from tornado.web import RequestHandler

from database import controller
from logger import log
from service.add_body import AddBodyService
from utils import handle_parse


class AddBodyHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

    async def post(self):
        data = self.request.body.decode(encoding='utf-8')
        try:
            d_data = loads(data)
        except JSONDecodeError as e:
            log.error(e)
            d_data = handle_parse(data)

        log.info(f"data {data}")
        sessionmaker = next(controller.get_session())
        svc = AddBodyService(session=sessionmaker)
        result = await svc.add(d_data)
        self.write(result)
