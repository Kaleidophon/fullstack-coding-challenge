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


def get_story(story_id):
    from hackerbabel.clients.mongodb_client import MongoDBClient
    mdb_client = MongoDBClient()
    story = mdb_client.find_document("id", story_id, "articles")
    return story


def get_stories():
    from hackerbabel.clients.mongodb_client import MongoDBClient
    mdb_client = MongoDBClient()
    stories = mdb_client.get_newest_documents("articles")
    stories.reverse()  # Because of the way jinja renders the stories
    return stories


def require_init(func):
    @wraps(func)
    def wrapping_func(*args, **kwargs):
        initialized = getattr(args[0], "initialized")

        if not initialized:
            raise Exception("Static class hasn't been initialized yet.")

        return func(*args, **kwargs)

    return wrapping_func
