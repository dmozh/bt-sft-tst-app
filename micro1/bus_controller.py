import pika
import pika.exceptions
from settings import settings
from logger import log
from time import sleep

credentials = pika.PlainCredentials(settings.rabbit_user, settings.rabbit_pwd)


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