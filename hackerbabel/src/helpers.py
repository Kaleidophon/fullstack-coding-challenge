# -*- coding: utf-8 -*-

"""
Module of small helper functions used throughout the project.
"""

# STD
from functools import wraps
import os
import types


def check_and_create_directory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)


def get_story(story_id):
    from hackerbabel.clients.mongodb_client import MongoDBClient
    from hackerbabel.clients.hackernews_client import HackerNewsClient

    mdb_client = MongoDBClient()
    hn_client = HackerNewsClient()
    story = mdb_client.find_document("id", story_id, "articles")
    story = hn_client.resolve_comment_ids(story)
    return story


def get_stories():
    from hackerbabel.clients.mongodb_client import MongoDBClient

    mdb_client = MongoDBClient()
    stories = mdb_client.get_newest_documents("articles")
    stories.reverse()  # Because of the way jinja renders the stories
    return stories


def get_config_from_py_file(config_path):
    config = types.ModuleType('config')
    config.__file__ = config_path
    try:
        with open(config_path) as config_file:
            exec(compile(config_file.read(), config_path, 'exec'),
                 config.__dict__)
    except IOError:
        pass  # Test will fail anyway
    keys = [key for key in dir(config) if key.isupper()]
    values = [getattr(config, key) for key in keys]
    return dict(zip(keys, values))


def require_init(func):
    @wraps(func)
    def wrapping_func(*args, **kwargs):
        initialized = getattr(args[0], "initialized")

        if not initialized:
            raise Exception("Static class hasn't been initialized yet.")

        return func(*args, **kwargs)

    return wrapping_func
