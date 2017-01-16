# -*- coding: utf-8 -*-

"""
Tests for flask app configuration.
"""

# STD
import os
import types
from unittest import TestCase

# EXT
from flask import Flask
from nose.tools import ok_

# PROJECT
from hackerbabel.src.configuration import config_selector

# CONSTANT
CONFIG_PATH = "../config.py"
OBLIGATORY_SETTINGS = {
    "PROPAGATE_EXCEPTIONS",
    "UNBABEL_API_URI",
    "UNBABEL_API_EMAIL",
    "UNBABEL_API_SECRET"
}


class ConfigurationTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(ConfigurationTestCase, self).__init__()

    def runTest(self):
        pass

    @staticmethod
    def check_settings():
        config = types.ModuleType('config')
        config.__file__ = CONFIG_PATH
        try:
            with open(CONFIG_PATH) as config_file:
                exec(compile(config_file.read(), CONFIG_PATH, 'exec'), config.__dict__)
        except IOError:
            pass  # Test will fail anyway

        # Check if most important settings are present
        for setting in OBLIGATORY_SETTINGS:
            ok_(setting in config)

        # Update with environment
        for setting in config:
            if setting in os.environ:
                config[setting] = os.environ[setting]

        # Check if flask uses all settings
        app = Flask(import_name=__name__)
        app = config_selector(app)

        for setting, value in config.iteritems():
            assert value == app.config[setting]
