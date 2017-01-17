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

    def __init__(self, *args, **kwargs):
        super(MongoDBClientTestCase, self).__init__()

    def runTest(self):
        _ids = self.test_add_document()
        self.test_find_document(_ids)
        self.test_newest_documents()
        self.test_update_documents(_ids)

    def test_add_document(self):
        documents = self.hn_client.get_top_stories()
        _ids = []

        for document in documents:
            report = self.mdb_client.add_document(document, "articles")
            ok_(report._WriteResult__acknowledged)
            _ids.append(str(report.inserted_id))

        return _ids

    def test_find_document(self, document_ids):
        shuffle(document_ids)
        for document_id in document_ids:
            result = self.mdb_client.find_document(
                "_id", document_id, "articles"
            )
            ok_(
                result is not None,
                "Document with _id {} was not found".format(document_id)
            )

    def test_newest_documents(self):
        # Add another round of documents, check if they're also listed as the
        # most recent ones
        documents = self.hn_client.get_top_stories()

        for document in documents:
            self.mdb_client.add_document(document, "articles")

        newest_documents = self.mdb_client.get_newest_documents("articles")

        titles = [document["titles"]["EN"]["title"] for document in documents]
        newest_titles = [
            document["titles"]["EN"]["title"]
            for document in newest_documents
        ]
        newest_titles.reverse()
        ok_(
            titles == newest_titles,
            "Newest documents weren't actually the most recent ones."
        )

    def test_update_documents(self, document_ids):
        document_id = choice(document_ids)
        old_document = self.mdb_client.find_document(
            "_id", document_id, "articles"
        )
        update = "Quite silly article"
        old_document["article_type"] = update

        report = self.mdb_client.update_document(
            "articles", document_id, {"article_type": update}
        )
        ok_(report["updatedExisting"] and report["ok"])
        new_document = self.mdb_client.find_document(
            "_id", document_id, "articles"
        )

        ok_(old_document == new_document)

    def setUp(self):
        config = get_config_from_py_file(CONFIG_PATH)
        config["MONGODB_NAME"] += "_test"  # Create special test database
        self.mdb_client = MongoDBClient()
        self.hn_client = HackerNewsClient()
        self.mdb_client.initialize(**config)
        self.hn_client.initialize(**config)

    def tearDown(self):
        collection = getattr(self.mdb_client.db, "articles")
        collection.remove({})

