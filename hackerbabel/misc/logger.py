# -*- coding: utf-8 -*-

"""
Setup logger.
"""

# STD
import sys
import logging

# PROJECT
from hackerbabel.misc.helpers import check_and_create_directory


def setup_logger(config):
    """
    Setup logger with information from configuration file

    @param config: app configuration
    @type config: dict or class
    """
    filename = config["LOGGER_FILE"]
    log_dir = '/'.join(filename.split('/')[0:-1]) + "/"

    check_and_create_directory(log_dir)

    level = config["LOGGER_LOGLEVEL"].upper()
    filemode = 'a'
    _format = '%(asctime)s %(name)8s %(module)15s %(funcName)12s %(' \
              'levelname)7s: %(message)s'
    _dateformat = '(%d.%m.%Y, %H:%M:%S)'

    logging.basicConfig(filename=filename, filemode=filemode, level=level,
                        format=_format, datefmt=_dateformat)

    logging.getLogger('urllib3')

    # Display log simultaneously on console
    if config["CONSOLE_LOGGING"]:
        add_terminal_logging(_format, level)


def add_terminal_logging(log_format, level=logging.DEBUG):
    logger = logging.getLogger()
    terminal_logger = logging.StreamHandler(sys.stdout)
    terminal_logger.setLevel(level)
    formatter = logging.Formatter(log_format)
    terminal_logger.setFormatter(formatter)
    logger.addHandler(terminal_logger)
