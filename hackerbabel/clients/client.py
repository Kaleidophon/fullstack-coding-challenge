# -*- coding: utf-8 -*-

"""
Superclass for different clients.
"""


class Client(object):
	client = None
	initialized = None

	@classmethod
	def initialize(cls, *init_args, **init_kwargs):
		cls.initialized = True
