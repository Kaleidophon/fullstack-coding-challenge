# -*- coding: utf-8 -*-

"""
Client used to access MongoDB
"""

# EXT
from pymongo import MongoClient
from bson.objectid import ObjectId

# PROJECT
from hackerbabel.clients.client import Client
from hackerbabel.src.helpers import require_init
from hackerbabel.src.schema import ArticleSchema


class MongoDBClient(Client):
    """
    Client to communicate to MongoDB via pymongo.
    """
    db = None
    schema = None
    number_of_stories = None

    @classmethod
    def initialize(cls, **init_kwargs):
        """
        Initialize the client.

        @param init_kwargs: Dictionary of init parameters, e.g. a config.
        @type init_kwargs: dict
        """
        username = init_kwargs.get("MONGODB_USER", "")
        password = init_kwargs.get("MONGODB_PASSWORD", "")
        host = init_kwargs.get("MONGODB_HOST", "localhost")
        port = init_kwargs.get("MONGODB_PORT", 27017)
        database = init_kwargs.get("MONGODB_NAME", "")
        options = init_kwargs.get("MONGODB_OPTIONS", "")
        cls.number_of_stories = init_kwargs.get("NUMBER_OF_STORIES", 10)

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
    def add_document(cls, document, collection_name, schema=None):
        """
        Add new document to a collection.

        @param document: Mongo DB document to be added.
        @type document: dict
        @param collection_name: Name of the collection the document should be
        added to.
        @type collection_name: str or unicode
        @param schema: Schema - if given - the document will be validated
        against
        @type schema: Hackerbabel.src.schema.Schema
        @return: Result report of insertion
        @rtype: object
        """
        collection = getattr(cls.db, collection_name)

        if schema:
            schema.validate(document)
        result = collection.insert_one(document, True)
        return result

    @classmethod
    @require_init
    def find_document(cls, key, value, collection_name, sort_direction=-1):
        """
        Find a document inside a collection.

        @param key: Attribute the document should possess
        @type key: str or unicode
        @param value: Value that should correspond to the key.
        @type value: type
        @param collection_name: Name of the collection the document should be
        added to.
        @type collection_name: str or unicode
        @param sort_direction: Sort direction if multiple documents with
        criterion exist.
        @type sort_direction: int
        @return: The first document matching the criteria or None
        @rtype: dict or None
        """
        collection = getattr(cls.db, collection_name)
        if key == "_id":
            value = ObjectId(value)
        result = [
            document for document in
            collection.find({key: value}).sort("_id", sort_direction)
        ]
        if len(result) == 0:
            return None
        return result[0]

    @classmethod
    @require_init
    def get_newest_documents(cls, collection_name):
        """
        Get the newest documents acquired during the last run of the daemon.

        @param collection_name: Name of the collection the document should be
        added to.
        @type collection_name: str or unicode
        @return: Newest documents
        @rtype: List
        """
        collection = getattr(cls.db, collection_name)
        newest_documents = [
            document for document in
            collection.find().sort("_id", -1).limit(cls.number_of_stories)
        ]
        return newest_documents

    @classmethod
    @require_init
    def update_document(cls, collection_name, document_id, updates):
        """
        Update an existing document.

        @param collection_name: Name of the collection the document should be
        added to.
        @type collection_name: str or unicode
        @param document_id: MongoDB ID of document (_id)
        @type document_id: int
        @param updates: Dictionary of updates as field -> new value
        @type updates: dict
        @return: MongoDB Update report
        @rtype: object
        """
        collection = getattr(cls.db, collection_name)
        report = collection.update(
            {"_id": ObjectId(document_id)},
            {"$set": updates},
        )
        return report
