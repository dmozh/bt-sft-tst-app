import pika
import pika.exceptions
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
from threading import Thread
from json import loads

from settings import settings
from logger import log
from time import sleep

from bus_event_handlers.add_event import AddEventHandler
from bus_event_handlers.delete_event import DeleteEventHandler
from bus_event_handlers.update_event import UpdateEventHandler

credentials = pika.PlainCredentials(settings.rabbit_user, settings.rabbit_pwd)



class BusReceiverController(Thread):
    def __init__(self):
        super().__init__()
        self.connection = None
        self.dsn = f"amqp://{settings.rabbit_user}:{settings.rabbit_pwd}@{settings.rabbit_host}/"
        self.engine = create_async_engine(
            f"postgresql+asyncpg://{settings.database_user}:{settings.database_pwd}@{settings.database_host}/{settings.database_name}",
            echo=False)

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

    async def callback(self, message: AbstractIncomingMessage):
        body = message.body.decode('utf-8')
        log.info(f" [x] {body}")
        try:
            body = loads(body)
            session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
            if body['event'] == 'add':
                handler = AddEventHandler(session=session)
                await handler.handle(body)
            if body['event'] == 'delete':
                handler = DeleteEventHandler(session=session)
                await handler.handle(body)
            if body['event'] == 'update':
                handler = UpdateEventHandler(session=session)
                await handler.handle(body)
        except Exception as e:
            log.error(f"Error {e}. Type {type(e)}")

    async def s(self):
        await self.get_connection()

        async with self.connection:
            log.info(f"Open channel in connection")
            channel = await self.connection.channel()
            queue = await channel.declare_queue('statistic_queue')
            log.info(f"Start consuming in statistic queue")
            await queue.consume(self.callback, no_ack=True)
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
