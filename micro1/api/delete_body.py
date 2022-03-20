from abc import ABC

from tornado.web import RequestHandler

from database import controller

from service.delete_body import DeleteBodyService


class DeleteBodyHandler(RequestHandler, ABC):
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

    async def delete(self, key):
        if key:
            sessionmaker = next(controller.get_session())
            svc = DeleteBodyService(session=sessionmaker)
            result = await svc.delete(key)
            self.write(result)