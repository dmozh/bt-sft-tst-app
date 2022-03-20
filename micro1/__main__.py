import tornado.ioloop
import tornado.web
from api.add_body import AddBodyHandler
from api.get_body import GetBodyHandler
from api.delete_body import DeleteBodyHandler
from api.upd_body import UpdateBodyHandler

from settings import settings

def make_app():
    route_prefix = "/api"
    return tornado.web.Application(
        [
            (rf"{route_prefix}/add", AddBodyHandler),
            (rf"{route_prefix}/get", GetBodyHandler),
            (rf"{route_prefix}/remove/([^/]+)?", DeleteBodyHandler),
            (rf"{route_prefix}/update/([^/]+)?", UpdateBodyHandler)
        ]
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(int(settings.server_port), settings.server_host)
    tornado.ioloop.IOLoop.current().start()