# -*- coding: utf-8 -*-

"""
Superclass for different clients.
"""

# STD
from abc import abstractmethod


class Client(object):
    """
    Small superclass for clients. Clients are created so they only have to be
    initialized once but can be instantiated later again without the need of
    giving its initialization data (e.g. the config) again.
    """
    client = None
    initialized = None

    @classmethod
    @abstractmethod
    def initialize(cls, **init_kwargs):
        """
        Initialize the client.

        @param init_kwargs: Dictionary of init parameters, e.g. a config.
        @type init_kwargs: dict
        """
        cls.initialized = True  # Should end with this statement
