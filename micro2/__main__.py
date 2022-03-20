import tornado.ioloop
import tornado.web
from api.get_body import GetBodyHandler

import asyncio
from logger import log
from settings import settings
from database import controller
from cache import r
from time import sleep
from bus_controller import BusReceiverController

import threading


def make_app():
    route_prefix = "/api"
    return tornado.web.Application(
        [
            (rf"{route_prefix}/statistic", GetBodyHandler),
        ]
    )


def start_app():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = make_app()
    app.listen(int(settings.server_port), settings.server_host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    log.info(f"Start bus thread")
    thread_bus = BusReceiverController()
    thread_bus.start()

    log.info(f"Start app thread")
    thread_app = threading.Thread(target=start_app)
    thread_app.daemon = True
    thread_app.start()

    log.info(f"App is working...")
    thread_app.join()
