import pika
import pika.exceptions
import asyncio

from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
from threading import Thread
from json import loads

from settings import settings
from logger import log
from time import sleep
from database import controller
from bus_event_handlers.add_event import AddEventHandler
from bus_event_handlers.delete_event import DeleteEventHandler
from bus_event_handlers.update_event import UpdateEventHandler

credentials = pika.PlainCredentials(settings.rabbit_user, settings.rabbit_pwd)


# def get_connection():
#     conn = pika.BlockingConnection(pika.ConnectionParameters(host="bus",
#                                                              virtual_host="/",
#                                                              credentials=credentials))
#     return conn


async def callback(message: AbstractIncomingMessage):
    body = message.body.decode('utf-8')
    try:
        body = loads(body)
        if body['event'] == 'add':
            # handle add event
            await AddEventHandler(session=next(controller.get_session())).handle(body)
        if body['event'] == 'delete':
            # handle delete event
            await DeleteEventHandler(session=next(controller.get_session())).handle(body)
        if body['event'] == 'update':
            # handle update event
            await UpdateEventHandler(session=next(controller.get_session())).handle(body)

    except Exception as e:
        log.error(f"Error {e}. Type {type(e)}")
    log.info(f" [x] {body}")


class BusReceiverController(Thread):
    def __init__(self):
        super().__init__()
        self.connection = None
        self.dsn = f"amqp://{settings.rabbit_user}:{settings.rabbit_pwd}@{settings.rabbit_host}/"

    async def get_connection(self):
        retry = True
        while retry:
            try:
                log.info(f"Try connect to rabbit: host={settings.rabbit_host}, user={settings.rabbit_user}")
                self.connection = await connect(self.dsn)
            except Exception as e:
                log.error("Connection error. Retry via 5 seconds")
                await asyncio.sleep(5)
            else:
                log.info(f"Connection successful")
                retry = False

    async def s(self):
        await self.get_connection()

        async with self.connection:
            log.info(f"Open channel in connection")
            channel = await self.connection.channel()
            queue = await channel.declare_queue('statistic_queue')
            log.info(f"Start consuming in statistic queue")
            await queue.consume(callback, no_ack=True)
            await asyncio.Future()

    def run(self) -> None:
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.run(self.s())


class BusSenderController:
    def __init__(self):
        retry = True
        while retry:
            try:
                log.info(f"Try connect to rabbit: host={settings.rabbit_host}, user={settings.rabbit_user}")
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.rabbit_host,
                                                                                    virtual_host="/",
                                                                                    credentials=credentials))
            except pika.exceptions.AMQPConnectionError as e:
                log.error("Connection error. Retry via 1 seconds")
                sleep(1)
            else:
                log.info(f"Connection successful")
                retry = False

    def __enter__(self):
        log.info(f"Return connection")
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.info(f"Close connection")
        self.connection.close()
