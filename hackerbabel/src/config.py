# -*- coding: utf-8 -*-

"""
Configuration file for whole Flask Application.

@note: All keys have to be UPPERCASED to get recognized as Flask configuration.
"""

# STD
import logging

# CONST
LOGGER = logging.getLogger(__name__)
DEFAULT_CONFIG_PATH = 'hackerbabel/config.py'  # Default config path


def config_selector(app):
    """
    Select the right configuration class, so Flask can import the right settings
    with from_object() method.
    """
    config_path = app.config.get("DEFAULT_CONFIG_PATH", DEFAULT_CONFIG_PATH)

    # Get config from file
    app.config.from_pyfile(config_path)

    # Overwrite with values from environment variables if given
    for key in app.config:
        app.config.from_envvar(key, silent=True)

    return app
