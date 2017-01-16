# -*- coding: utf-8 -*-

"""
Create Flask application, setup everything.
"""

# STD
import logging

# EXT
from flask import Flask
from flask_bootstrap import Bootstrap

# PROJECT
from hackerbabel.clients.mongodb_client import MongoDBClient
from hackerbabel.clients.hackernews_client import HackerNewsClient
from hackerbabel.clients.unbabel_client import UnbabelClient

from hackerbabel.src.config import config_selector
from hackerbabel.src.daemon import HackerNewsDaemon
from hackerbabel.src.error_handlers import register_error_handlers
from hackerbabel.src.logger import setup_logger

from hackerbabel.views.index import INDEX
from hackerbabel.views.dashboard import DASHBOARD
from hackerbabel.views.comment_section import COMMENT_SECTION

# CONST
LOGGER = logging.getLogger(__name__)


def setup_app():
    """
    Setup and run Flask app

    @return: app which could be launched immediately
    @rtype: Flask
    """
    # 1 Create Flask application
    app = Flask(
        import_name=__name__,
        template_folder="templates",
        static_folder="static"
    )

    # 2 Update the apps configuration
    app = config_selector(app)
    register_error_handlers(app)

    # 3 Set up logger
    setup_logger(app.config)
    LOGGER.info("Set up app & logger.")

    # 4 Init clients
    init_clients(app.config)

    # 5 Init Daemon
    start_daemon(app.config)

    # 6 Register blueprints
    register_blueprints(app)
    Bootstrap(app)

    return app


def init_clients(config):
    clients = {
        MongoDBClient(), HackerNewsClient(), UnbabelClient()
    }

    for client in clients:
        client.initialize(**config)

    LOGGER.info(
        "Initiated {} clients: {}.".format(
            len(clients),
            ", ".join([type(client).__name__ for client in clients])
        )
    )


def register_blueprints(app):
    blueprints = {INDEX, DASHBOARD, COMMENT_SECTION}

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def start_daemon(config):
    interval = config.get("REFRESH_INTERVAL", 600)
    hn_daemon = HackerNewsDaemon(interval)
    hn_daemon.run()
    LOGGER.info("Started daemon with time interval {}.".format(interval))
