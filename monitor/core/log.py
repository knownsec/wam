#!/usr/bin/env python
# coding: utf-8

# __buildin__ modules
import logging

from logging.handlers import RotatingFileHandler

# monitor modules
from monitor.core.settings import LOG_PATH


class LogFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: '%(asctime)s [DEBUG] %(message)s',
        logging.INFO: '%(asctime)s [INFO] %(message)s',
        logging.WARNING: '%(asctime)s [WARNING] %(message)s',
        logging.ERROR: '%(asctime)s [ERROR] %(message)s',
        logging.CRITICAL: '%(asctime)s [CRITICAL] %(message)s',
        'DEFAULT': '%(asctime)s [GENERATION] %(message)s'
    }

    def __init__(self):
        logging.Formatter.__init__(self)
        self.datefmt = '%Y-%m-%d %H:%M:%S'

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)

file_handler = RotatingFileHandler(LOG_PATH, mode='0', maxBytes=5*1024*1024)
file_handler.setFormatter(LogFormatter())
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(LogFormatter())
stream_handler.setLevel(logging.DEBUG)

logger = logging.getLogger('wamlog')
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
