# -*- coding: utf-8 -*-

"""
Module of small helper functions used throughout the project.
"""

# STD
from functools import wraps
import os
import types


def check_and_create_directory(directory):
    """
    Check if an directory exists and if no, create it.

    @param directory: Directory in question.
    @type directory: str or unicode
    """
    if not os.path.isdir(directory):
        os.makedirs(directory)


def get_story(story_id, story_collection):
    """
    Retrieve a specific story form the database via its Hacker News story id.

    @param story_id: Hacker News story id.
    @type story_id: int
    @param story_collection: Name of the collections the stories are stored in.
    @type story_collection: str or unicode
    @return: Story
    @rtype: dict
    """
    from hackerbabel.clients.mongodb_client import MongoDBClient
    from hackerbabel.clients.hackernews_client import HackerNewsClient

    mdb_client = MongoDBClient()
    hn_client = HackerNewsClient()
    story = mdb_client.find_document("id", story_id, story_collection)
    story = hn_client.resolve_comment_ids(story)
    return story


def get_stories(story_collection):
    """
    Get the stories that should be rendered on the starting page.

    @param story_collection: Name of the collections the stories are stored in.
    @type story_collection: str or unicode
    @return: Most recent stories.
    @rtype: list
    """
    from hackerbabel.clients.mongodb_client import MongoDBClient

    mdb_client = MongoDBClient()
    stories = mdb_client.get_newest_documents(story_collection)
    stories.reverse()  # Because of the way jinja2 renders the stories
    return stories


def get_config_from_py_file(config_path):
    """
    Load a configuration from a .py file.

    @param config_path: Path to configuration file.
    @type config_path: str or unicode
    @return: Config as dict.
    @rtype: dict
    """
    config = types.ModuleType('config')
    config.__file__ = config_path
    try:
        with open(config_path) as config_file:
            exec(compile(config_file.read(), config_path, 'exec'),
                 config.__dict__)
    except IOError:
        pass  # Test will fail anyway
    return {
        key: getattr(config, key) for key in dir(config) if key.isupper()
    }


def require_init(func):
    """
    Require the user to initialize a class once through the initialize()
    function before being able to use the function decorated with require_init
    (Makes sure no Exception is thrown because data the class operates on is
    missing).

    @param func: Decorated function
    @type func: func
    @return: Wrapping function
    @rtype: func
    """
    @wraps(func)
    def wrapping_func(*args, **kwargs):
        initialized = getattr(args[0], "initialized")

        if not initialized:
            raise Exception("Static class hasn't been initialized yet.")

        return func(*args, **kwargs)

    return wrapping_func
