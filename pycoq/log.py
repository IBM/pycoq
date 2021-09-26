"""
pycoq methods to interact with logging module
"""


import logging

import pycoq.config

def logging_level(a: int):
    ''' returns loggig level '''
    return {1: logging.CRITICAL,
            2: logging.ERROR,
            3: logging.WARNING,
            4: logging.INFO,
            5: logging.DEBUG}[a]

def config_logging():
    logging.basicConfig(
        filename=pycoq.config.log_filename(),
        filemode='a',
        format=('%(asctime)s - %(process)d - %(name)s'
                '- %(levelname)s - %(message)s'),
        level=logging_level(pycoq.config.log_level()))
    
def debug(msg: str):
    logging.debug(msg)

def info(msg: str):
    logging.info(msg)

def warning(msg: str):
    logging.warning(msg)
    
def error(msg: str):
    logging.error(msg)

def critical(msg):
    logging.critical(msg)


config_logging()


