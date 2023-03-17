import json
import logging
import logging.config
import os
import sys


def log_config(name, host, port):
    if not os.path.exists("log"):
        os.makedirs("log")
    setup = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(process)d %(thread)d %(asctime)s %(levelname)s %(name)s %(filename)s %(funcName)s %(lineno)d: %(message)s',
                'datefmt': '%Y/%m/%d %H:%M:%S'
            },
        },
        'handlers': {
            'consoleHandler': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            },
            'timeHandler': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'standard',
                'filename': f'log/{name}.log',
                'when': 'midnight',
                'interval': 1,
                'encoding':'utf-8'
            },
            'tcpHandler': {
                'class': 'logging.handlers.SocketHandler',
                'host': host,
                'port': port
            }
        },
        'loggers': {
            '':{
                'handlers': ['consoleHandler',
                #'tcphandler',
                'timeHandler'
                 ],
                'level': 'INFO',
            }
        }
    }

    logging.config.dictConfig(setup)


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 0000
    log_config('test',host,port)
    logger = logging.getLogger(f'logger_test')
    logger.info("zhenghao test")
