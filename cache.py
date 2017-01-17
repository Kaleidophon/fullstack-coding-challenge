# -*- coding: utf-8 -*-

"""
Simple caching.
"""

# EXT
from flask_cache import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
