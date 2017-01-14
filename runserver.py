# -*- coding: utf-8 -*-

"""
Create Flask application, setup everything and run it.
"""

# STD
import logging

# EXT
from flask import Flask

# PROJECT
from misc.config import config_selector
from misc.error_handlers import register_error_handlers
from misc.logger import setup_logger

# CONST
LOGGER = logging.getLogger(__name__)


def start_app():
    """
    Setup and run Flask app

    @return: app which could be launched immediately
    @rtype: Flask
    """
    # 1 Create Flask application
    app = Flask(import_name=__name__)

    # 2 Update the apps configuration
    app = config_selector(app)
    register_error_handlers(app)

    # 3 Configure access to database
    # DBAccess.prepare(**config.py)  # TODO: Implement this

    # 4 Set up logger
    setup_logger(app.config)
    LOGGER.info("Set up app & logger.")

    # 5 Run app
    app.run(use_reloader=False)
    LOGGER.info("App is running!")

    return app

if __name__ == "__main__":
    start_app()
