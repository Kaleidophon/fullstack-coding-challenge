# -*- coding: utf-8 -*-

"""
Simple daemon that gets regularly gets Hacker News' top news articles and
feeds them into MongoDB.
"""

# STD
import logging
import json
from time import sleep
from threading import Thread

# PROJECT
from hackerbabel.clients.hackernews_client import HackerNewsClient
from hackerbabel.clients.unbabel_client import UnbabelClient
from hackerbabel.clients.mongodb_client import MongoDBClient

# CONST
LOGGER = logging.getLogger(__name__)


class SimpleDaemon(object):

    def __init__(self, daemon_func, daemon_args, interval, daemonize=True):
        self.daemon_func = daemon_func
        self.daemon_args = daemon_args
        self.interval = interval
        self.mdb_client = MongoDBClient()
        self.daemonize = daemonize
        self.thread = None

    def run(self):
        self.thread = Thread(target=self.daemon_func, args=self.daemon_args)
        self.thread.daemon = self.daemonize
        self.thread.start()


class HackerNewsDaemon(SimpleDaemon):

    def __init__(self, interval, target_langs):
        self.hn_client = HackerNewsClient()
        self.target_langs = target_langs

        super(HackerNewsDaemon, self).__init__(
            self.refresh_top_stories, tuple(), interval
        )

    def refresh_top_stories(self, *args):
        while True:
            _ids = set()
            for document in self.hn_client.get_top_stories():
                title = document["titles"]["EN"]["title"]
                report = self.mdb_client.add_document(document, "articles")
                _ids.add((str(report.inserted_id), title))

            # Start translation processes
            for _id, title in _ids:
                for target_lang in self.target_langs:
                    ub_daemon = UnbabelDaemon(
                        self.interval, _id, target_lang, title
                    )
                    ub_daemon.run()
            sleep(self.interval)


class UnbabelDaemon(SimpleDaemon):

    def __init__(self, interval, document_id, target_language, title):
        self.ub_client = UnbabelClient()
        self.title = title

        logging.info(
            u"New thread trying to translate '{title}' into {lang}".format(
                title=self.title, lang=target_language
            )
        )

        # Do initial request
        response = None
        status_code = 404
        while status_code != 201 and status_code != 200:
            response = self.ub_client.make_translation_request(
                self.title, target_language
            )
            status_code = response.status_code

        response_data = json.loads(response.content)
        uid = response_data["uid"]

        super(UnbabelDaemon, self).__init__(
            self.translate_title, (uid, document_id, target_language),
            interval,
            daemonize=False
        )

    def translate_title(self, uid, document_id, target_language):
        response_data = None
        status = "new"

        self._change_story_translation_status(
            document_id, target_language, "pending"
        )

        # Check translation status
        while status != "completed":
            sleep(self.interval/10.0)
            response = self.ub_client.check_translation_status(uid)
            response_data = json.loads(response.content)
            status = response_data["status"]

        translated_text = response_data["translatedText"]

        logging.info(
            u"Translation complete!\n'{title}' --({lang})--> '{transtitle}'".format(
                title=self.title, lang=target_language,
                transtitle=translated_text
            )
        )

        self._change_story_translation_status(
            document_id, target_language, "done"
        )
        self._add_translated_story_title(
            document_id, target_language, translated_text
        )

    def _change_story_translation_status(self, document_id, language,
                                         new_status):
        self.mdb_client.update_document(
            "articles",
            document_id,
            updates={
                "titles.{}.translation_status".format(language): new_status
            }
        )

    def _add_translated_story_title(self, document_id, language,
                                    translated_title):
        self.mdb_client.update_document(
            "articles",
            document_id,
            updates={
                "titles.{}.title".format(language): translated_title
            }
        )
