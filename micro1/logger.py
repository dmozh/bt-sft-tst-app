import logging, logging.config
from os import makedirs
from os.path import exists, isfile
from settings import settings
from datetime import datetime

__LOGS_PATH = "./logs"
__FILE_NAME = f"{datetime.today().strftime('%Y-%m-%d')}_log.log"

__LEVEL = "DEBUG" if settings.DEBUG else "INFO"


class LowPassFilter:
    """
    - CRITICAL = 50
    - FATAL = CRITICAL
    - ERROR = 40
    - WARNING = 30
    - WARN = WARNING
    - INFO = 20
    - DEBUG = 10
    - NOTSET = 0
    """
    def __init__(self, level):
        self.__level = level

    def filter(self, log):
        return log.levelno <= self.__level


class HighPassFilter:
    """
    - CRITICAL = 50
    - FATAL = CRITICAL
    - ERROR = 40
    - WARNING = 30
    - WARN = WARNING
    - INFO = 20
    - DEBUG = 10
    - NOTSET = 0
    """
    def __init__(self, level):
        self.__level = level

    def filter(self, log):
        return log.levelno >= self.__level



__CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "verbosefilter": {
          "()": LowPassFilter,
          "level": 10
        },
        "infofilter": {
          "()": LowPassFilter,
          "level": 20
        },
        "warnfilter": {
          "()": HighPassFilter,
          "level": 30
        }
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(threadName)s - %(levelname)s - %(pathname)s - in line %(lineno)d \n%(message)s\n"
        },
        "debug": {
            "format": "[%(asctime)s] - [%(threadName)s in %(processName)s] - "
                      "%(levelname)s - %(pathname)s - in line %(lineno)d \n%(message)s\n"
        },
        "verbose": {
            "format": "[%(asctime)s] - "
                      "[%(processName)s -  id %(process)-2s] - "
                      "[%(threadName)s - id %(thread)s] - "
                      "%(levelname)s - %(pathname)s - in line %(lineno)d \n%(message)s\n"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "verbose",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "filters": ["infofilter"]
        },
        "console_err": {
            "level": "WARNING",
            "formatter": "verbose",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "filters": ["warnfilter"]
        },
        "console_debug": {
            "level": "DEBUG",
            "formatter": "verbose",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "filters": ["verbosefilter"]
        },
        "file_handler": {
            "level": "DEBUG",
            "formatter": "verbose",
            "class": "logging.handlers.RotatingFileHandler",
            "encoding": "utf-8",
            "filename": f"{__LOGS_PATH}/{__FILE_NAME}",
            "maxBytes": 1024*1024,
            # "backupCount": 1
        },
    },
    "loggers": {
        "": {
            "handlers": ["file_handler"],
            "level": __LEVEL,
            "propagate": False
        },
        "default": {
            "handlers": ["console", "console_err", "console_debug"],
            "level": __LEVEL,
            "propagate": True
        }
    }
}


if exists(__LOGS_PATH):
    if not isfile(f"{__LOGS_PATH}/{__FILE_NAME}"):
        open(f"{__LOGS_PATH}/{__FILE_NAME}", 'w', encoding='utf8')
else:
    makedirs(__LOGS_PATH)

if 'logger' in __name__:
    logging.config.dictConfig(__CONFIG)
    log = logging.getLogger("default")
    # log = logging.getLogger("debug")
