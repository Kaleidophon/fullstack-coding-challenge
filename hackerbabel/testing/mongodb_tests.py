# -*- coding: utf-8 -*-

"""
Tests for the UnbabelClient.
"""

# STD
from random import shuffle, choice
from unittest import TestCase

# EXT
from nose.tools import ok_

# PROJECT
from hackerbabel.clients.mongodb_client import MongoDBClient
from hackerbabel.clients.hackernews_client import HackerNewsClient
from hackerbabel.src.helpers import get_config_from_py_file
from hackerbabel.testing.configuration_tests import CONFIG_PATH


class MongoDBClientTestCase(TestCase):
    """
    Test the function of the MongoDB client.
    """
    def __init__(self, *args, **kwargs):
        super(MongoDBClientTestCase, self).__init__()

    def runTest(self):
        _ids = self.test_add_document()
        self.test_find_document(_ids)
        self.test_newest_documents()
        self.test_update_documents(_ids)

    def test_add_document(self):
        """
        Test whether an document gets added to MongoDB correctly.
        """
        documents = self.hn_client.get_top_stories()
        _ids = []

        # TODO: Create story fixtures to save time
        for document in documents:
            report = self.mdb_client.add_document(
                document, self.story_collection
            )
            ok_(report._WriteResult__acknowledged)
            _ids.append(str(report.inserted_id))

        return _ids

    def test_find_document(self, document_ids):
        """
        Test if an existing document can be found in the database.

        @param document_ids: List of document IDs that are going to be looked
        for.
        @type document_ids: list
        """
        shuffle(document_ids)
        for document_id in document_ids:
            result = self.mdb_client.find_document(
                "_id", document_id, self.story_collection
            )
            ok_(
                result is not None,
                "Document with _id {} was not found".format(document_id)
            )

    def test_newest_documents(self):
        """
        Test if the the newest documents given by the client are the actual
        newest ones from the Hacker News client.
        """
        # Add another round of documents, check if they're also listed as the
        # most recent ones
        documents = self.hn_client.get_top_stories()

        for document in documents:
            self.mdb_client.add_document(document, self.story_collection)

        newest_documents = self.mdb_client.get_newest_documents(
            self.story_collection
        )

        titles = [
            document["titles"][self.source_lang]["title"]
            for document in documents
        ]
        newest_titles = [
            document["titles"][self.source_lang]["title"]
            for document in newest_documents
        ]
        newest_titles.reverse()
        ok_(
            titles == newest_titles,
            "Newest documents weren't actually the most recent ones."
        )

    def test_update_documents(self, document_ids):
        """
        Test if documents get updated correctly.

        @param document_ids: Document IDs that one ID will be sampled from.
        @type document_ids: list
        """
        document_id = choice(document_ids)
        old_document = self.mdb_client.find_document(
            "_id", document_id, self.story_collection
        )
        update = "Quite silly article"
        old_document["article_type"] = update

        report = self.mdb_client.update_document(
            self.story_collection, document_id, {"article_type": update}
        )
        ok_(report["updatedExisting"] and report["ok"])
        new_document = self.mdb_client.find_document(
            "_id", document_id, self.story_collection
        )

        ok_(old_document == new_document)

    def setUp(self):
        self.config = get_config_from_py_file(CONFIG_PATH)
        self.config["MONGODB_NAME"] += "_test"  # Create special test database
        self.mdb_client = MongoDBClient()
        self.hn_client = HackerNewsClient()
        self.mdb_client.initialize(**self.config)
        self.hn_client.initialize(**self.config)
        self.story_collection = self.config["STORY_COLLECTION"]
        self.source_lang = self.config["SOURCE_LANGUAGE"]

    def tearDown(self):
        collection = getattr(self.mdb_client.db, self.story_collection)
        collection.remove({})

