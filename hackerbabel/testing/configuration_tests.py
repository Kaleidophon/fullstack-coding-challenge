# -*- coding: utf-8 -*-

"""
Tests for flask app configuration.
"""

# STD
import os
from unittest import TestCase

# EXT
from flask import Flask
from nose.tools import ok_

# PROJECT
from hackerbabel.src.configuration import config_selector, DEFAULT_CONFIG_PATH
from hackerbabel.src.helpers import get_config_from_py_file

# CONSTANT
OBLIGATORY_SETTINGS = {
    "PROPAGATE_EXCEPTIONS",
    "UNBABEL_API_URI",
    "UNBABEL_API_EMAIL",
    "UNBABEL_API_SECRET"
}

CONFIG_PATH = "hackerbabel/config.py"


class ConfigurationTestCase(TestCase):
    """
    Testing the app configuration.
    """
    def __init__(self, *args, **kwargs):
        super(ConfigurationTestCase, self).__init__()

    def runTest(self):
        self.check_settings()

    @staticmethod
    def check_settings():
        """
        Check if config is loaded into Flask app correctly and contains specific
        obligatory parameters.
        """
        config = get_config_from_py_file(CONFIG_PATH)

        # Check if most important settings are present
        for setting in OBLIGATORY_SETTINGS:
            ok_(setting in config.keys(), "{} not in settings.".format(setting))

        # Update with environment
        for setting in config:
            if setting in os.environ:
                config[setting] = os.environ[setting]

        # Check if flask uses all settings
        app = Flask(import_name=__name__)
        app = config_selector(app, config_path="../" + DEFAULT_CONFIG_PATH)

        for setting, value in config.iteritems():
            assert value == app.config[setting]
