# -*- coding: utf-8 -*-

"""
Registering handlers for specific error classes.
"""

# STD
import datetime
import logging
import traceback

# CONST
LOGGER = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    Register error handlers for current app.

    @param app: Current flask app
    @type app: flask.app.Flask
    """

    @app.errorhandler(404)
    def page_not_found(exception):
        # TODO: Make this prettier
        return "Sorry! This page doesn't exist.", 404

    @app.errorhandler(Exception)
    def handle_any_exception(error):
        """
        Handles any remaining exception so the app doesn't stop running.
        @param error: Raised exception
        @type error: Exception
        """
        # Create a log entry
        log_entry = [
            u"INTERNAL SERVER ERROR",
            u"Time: {}".format(datetime.datetime.now().isoformat()),
            u"Error type: {}".format(type(error)),
            u"Error message: {}".format(error.message),
            u"Traceback: "
        ]
        log_entry.extend(traceback.format_exc().split("\n"))

        LOGGER.error(
            "\n".join(log_entry)
        )
