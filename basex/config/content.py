__author__ = 'ziyan.yin'
__describe__ = 'global content'

import logging

from loguru import logger
import os
import yaml

from ..common import objectutils
from ..core.logstash import LoggerHandler

env = 'application%s.yaml'
server: dict = {}
project: dict = {}
session: dict = {}
log: dict = {}
db: dict = {}
cache: dict = {}
extends: dict = {}


def init(stage=""):
    global server
    global project
    global session
    global log
    global db
    global cache
    global extends

    path = os.path.join(env % ("-" + stage if stage else ""))
    if os.path.exists(path):
        with open(path, encoding='utf-8') as fs:
            data = objectutils.default_if_null(yaml.load(fs, Loader=yaml.FullLoader), {'config': {}})
        server = server | data['config']['server']
        project = project | data['config']['project']
        session = session | data['config']['session']
        log = log | data['config']['log']
        log['sink'] = os.path.join(project['log_dir'], log['filename'])
        del log['filename']
        db = db | data['config']['db']
        cache = cache | data['config']['cache']
        extends = extends | {
            key: value for key, value in data['config'].items() if key not in (
                'server', 'project', 'session', 'log', 'db', 'cache'
            )
        }
    else:
        raise FileNotFoundError(path)

    try:
        __import__(db['package'])
    except ImportError as ex:
        logger.exception(ex)
        raise

    logging.getLogger().handlers = [LoggerHandler()]
