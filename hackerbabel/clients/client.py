# -*- coding: utf-8 -*-

"""
Superclass for different clients.
"""

# STD
from abc import abstractmethod

class Client(object):
    """
    Small superclass for clients.
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
