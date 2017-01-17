# -*- coding: utf-8 -*-

"""
Test daemons.
"""

# STD
from random import choice

# EXT
from nose.tools import ok_

# PROJECT
from hackerbabel.clients.unbabel_client import UnbabelClient
from hackerbabel.src.daemon import UnbabelDaemon
from hackerbabel.testing.mongodb_tests import MongoDBClientTestCase


class DaemonTestCase(MongoDBClientTestCase):
    """
    Test the daemon.

    @note: Currently broken - gets executed more than once.
    """
    def __init__(self, *args, **kwargs):
        super(DaemonTestCase, self).__init__()

    def runTest(self):
        pass
        # TODO: Fix this: Somehow this gets called four times?
        # self.test_translate_title()

    def test_translate_title(self):
        """
        Tests if a title's translation and update of its translation status
        gets done correctly.
        """
        # Prepare
        interval = self.config["REFRESH_INTERVAL"]
        document_id = choice(self._ids)
        document = self.mdb_client.find_document(
            "_id", document_id, "articles"
        )
        title = document["titles"]["EN"]["title"]
        target_language = choice(self.config["TARGET_LANGUAGES"])

        # Start daemon
        ub_daemon = UnbabelDaemon(interval, document_id, target_language, title)
        ub_daemon.run()
        ub_daemon.thread.join()
        ub_daemon.thread.exit()

        translated_document = self.mdb_client.find_document(
            "_id", document_id, "articles"
        )
        translation_status = translated_document["titles"][target_language][
            "translation_status"
        ]
        translated_title = translated_document["titles"][target_language][
            "title"
        ]

        # Check whether title was translated
        ok_(translation_status == "done")
        ok_(translated_title != "###")

        return

    def setUp(self):
        super(DaemonTestCase, self).setUp()
        self._ids = []
        documents = self.hn_client.get_top_stories()

        for document in documents:
            report = self.mdb_client.add_document(document, "articles")
            ok_(report._WriteResult__acknowledged)
            self._ids.append(str(report.inserted_id))

        self.ub_client = UnbabelClient()
        self.ub_client.initialize(**self.config)

    def tearDown(self):
        super(DaemonTestCase, self).tearDown()
