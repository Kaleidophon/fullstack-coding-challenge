# -*- coding: utf-8 -*-

"""
Configuration file for whole Flask Application.

@note: All keys have to be UPPERCASED to get recognized as Flask configuration.
"""

# STD
import logging

# CONST
LOGGER = logging.getLogger(__name__)
DEFAULT_CONFIG_PATH = 'config.py'


def config_selector(app, config_path=DEFAULT_CONFIG_PATH):
    """
    Select the right configuration class, so Flask can import the right settings
    with from_object() method.

    @param app: Flask app the configuration should be added to.
    @type app: flask.Flask
    @param config_path: Path to configuration file.
    @type config_path: str or unicode.
    @return: App with config.
    @rtype: flask.Flask
    """

    # Get config from file
    app.config.from_pyfile(config_path)

    # Overwrite with values from environment variables if given
    for key in app.config:
        app.config.from_envvar(key, silent=True)

    return app
