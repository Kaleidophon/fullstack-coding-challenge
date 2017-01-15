# -*- coding: utf-8 -*-

"""
Client used to access MongoDB
"""

# EXT
from pymongo import MongoClient

# PROJECT
from hackerbabel.clients.client import Client
from hackerbabel.misc.helpers import require_init
from hackerbabel.misc.schema import ArticleSchema


class MongoDBClient(Client):
    db = None
    schema = None

    @classmethod
    def initialize(cls, **init_kwargs):
        username = init_kwargs.get("username", "")
        password = init_kwargs.get("password", "")
        host = init_kwargs.get("host", "localhost")
        port = init_kwargs.get("port", 27017)
        database = init_kwargs.get("database", "")
        options = init_kwargs.get("options", "")

        credentials = ""
        if username and password:
            credentials = "{user}:{pw}@".format(user=username, pw=password)
        if options:
            if type(options) == list:
                options = "/?" + "&".join(options)
            else:
                options = "/?" + options

        uri = "mongodb://{}{}:{}{}".format(
            credentials, host, port, options
        )
        cls.client = MongoClient(uri)
        cls.db = getattr(cls.client, database)
        cls.schema = ArticleSchema()
        cls.initialized = True

    @classmethod
    @require_init
    def add_document(cls, document, collection_name):
        collection = getattr(cls.db, collection_name)
        cls.schema.validate(document)
        result = collection.insert_one(document)
        return result

    @classmethod
    @require_init
    def add_documents(cls, documents, collection_name):
        collection = getattr(cls.db, collection_name)

        for document in documents:
            cls.schema.validate(document)

        result = collection.insert_many(documents)
        return result





