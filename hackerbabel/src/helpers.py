# -*- coding: utf-8 -*-

"""
Module of small helper functions used throughout the project.
"""

# STD
from functools import wraps
import os


def check_and_create_directory(directory):
	if not os.path.isdir(directory):
		os.makedirs(directory)


def require_init(func):
	@wraps(func)
	def wrapping_func(*args, **kwargs):
		initialized = getattr(args[0], "initialized")

		if not initialized:
			raise Exception("Static class hasn't been initialized yet.")

		return func(*args, **kwargs)

	return wrapping_func
