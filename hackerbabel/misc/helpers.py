# -*- coding: utf-8 -*-

"""
Module of small helper functions used throughout the project.
"""

# STD
import os


def check_and_create_directory(directory):
	if not os.path.isdir(directory):
		os.makedirs(directory)
