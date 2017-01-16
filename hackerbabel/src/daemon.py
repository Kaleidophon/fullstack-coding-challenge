# -*- coding: utf-8 -*-

"""
Simple daemon that gets regularly gets Hacker News' top news articles and
feeds them into MongoDB.
"""

# STD
import json
from time import sleep
from threading import Thread

# PROJECT
from hackerbabel.clients.hackernews_client import HackerNewsClient
from hackerbabel.clients.unbabel_client import UnbabelClient
from hackerbabel.clients.mongodb_client import MongoDBClient


class SimpleDaemon(object):

    def __init__(self, daemon_func, daemon_args, interval):
        self.daemon_func = daemon_func
        self.daemon_args = daemon_args
        self.interval = interval
        self.mdb_client = MongoDBClient()

    def run(self):
        first = Thread(target=self.daemon_func, args=(self.daemon_args, ))
        first.daemon = True
        first.start()


class HackerNewsDaemon(SimpleDaemon):

    def __init__(self, interval):
        self.hn_client = HackerNewsClient()

        super(HackerNewsDaemon, self).__init__(
            self.refresh_top_stories, tuple(), interval
        )

    def refresh_top_stories(self, *args):
        while True:
            for document in self.hn_client.get_top_stories():
                self.mdb_client.add_document(document, "articles")
            sleep(self.interval)


class UnbabelDaemon(SimpleDaemon):

    def __init__(self, interval, story_id, title, target_language):
        self.ub_client = UnbabelClient()

        # Do initial request
        response = None
        status_code = 404
        while status_code != 200:
            response = self.ub_client.make_translation_request(
                title, target_language
            )
            status_code = response.status_code

        response_data = json.loads(response.data)
        uid = response_data["uid"]

        super(UnbabelDaemon, self).__init__(
            self.translate_title, (uid, story_id), interval
        )

    def translate_title(self, uid, story_id):
        response = None
        status = "new"

        self._change_story_translation_status(story_id, "pending")

        # Check translation status
        while status != "completed":
            sleep(self.interval/10.0)
            response = self.ub_client.check_translation_status(uid)
            response_data = json.loads(response.data)
            status = response_data["status"]

        response_data = json.loads(response.data)
        target_lang = response_data["target_language"]
        translated_text = response_data["translatedText"]

        self._change_story_translation_status(story_id, "done")
        self._add_translated_story_title(story_id, target_lang, translated_text)

    def _change_story_translation_status(self, story_id, new_status):
        pass

    def add_translated_story_title(self, story_id, language, translated_title):
        pass

