# -*- coding: utf-8 -*-

"""
Module defining simple daemons to get Hacker News on a regular basis and
translate them.
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
    """
    Daemon superclass.
    """
    def __init__(self, daemon_func, daemon_args, interval, daemonize=True):
        """
        Initializer.

        @param daemon_func: Function the daemon should execute.
        @type daemon_func: func
        @param daemon_args: Args for daemon func.
        @type daemon_args: tuple
        @param interval: Time interval between function executions.
        @type interval: int
        @param daemonize: Daemonize thread. See UnbabelDaemon.
        @type daemonize: bool
        """
        self.daemon_func = daemon_func
        self.daemon_args = daemon_args
        self.interval = interval
        self.mdb_client = MongoDBClient()
        self.daemonize = daemonize
        self.thread = None

    def run(self):
        """
        Run daemon function.
        """
        self.thread = Thread(target=self.daemon_func, args=self.daemon_args)
        self.thread.daemon = self.daemonize
        self.thread.start()


class HackerNewsDaemon(SimpleDaemon):
    """
    Daemon that retrieves the most recent Hacker News and creates threads to
    translate the titles.
    """
    def __init__(self, interval, source_lang, target_langs, story_collection):
        self.hn_client = HackerNewsClient()
        self.source_lang = source_lang
        self.target_langs = target_langs
        self.story_collection = story_collection

        super(HackerNewsDaemon, self).__init__(
            self.refresh_top_stories, tuple(), interval
        )

    def refresh_top_stories(self, *args):
        """
        Refresh the current Hacker news stories.

        @param args: Argument of functions - in this case, none.
        @type args: tuple
        """
        while True:
            _ids = set()
            for document in self.hn_client.get_top_stories():
                title = document["titles"][self.source_lang]["title"]
                story_id = document["id"]

                # Check if story already exists -> maybe no need for
                # translation / comment resolving
                result = self.mdb_client.find_document(
                    "id", story_id, self.story_collection, 1
                )
                if result:
                    document["titles"] = result["titles"]
                    if document["descendants"] == result["descendants"]:
                        document["comments"] = result["comments"]

                report = self.mdb_client.add_document(
                    document, self.story_collection
                )

                if not result:
                    _ids.add((str(report.inserted_id), title))

            # Start translation processes
            for _id, title in _ids:
                for target_lang in self.target_langs:
                    ub_daemon = UnbabelDaemon(
                        self.interval, _id, target_lang, title,
                        self.story_collection
                    )
                    ub_daemon.run()
            sleep(self.interval)


class UnbabelDaemon(SimpleDaemon):
    """
    Unbabel daemon that is called by HackerNewsDaemon and translates one
    Hacker News story title into one target language.

    @note: This is not technically a Daemon, just a regular thread. But it was
    helpful letting this inherit from SimpleDaemon.
    """
    def __init__(self, interval, document_id, target_language, title,
                 story_collection):
        """
        Initializer.

        @param interval: Time interval between function executions.
        @type interval: int
        @param document_id: MongoDB ID of document (_id)
        @type document_id: int
        @param target_language: Language the text should be translated into.
        @type target_language: str or unicode
        @param title: News title to be translated.
        @type title: str or unicode.
        """
        self.ub_client = UnbabelClient()
        self.title = title
        self.story_collection = story_collection

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
        """
        Translate a story title.

        @param uid: Unique Unbabel API job idea.
        @type uid: str or unicode
        @param document_id: MongoDB ID of document (_id)
        @type document_id: int
        @param target_language: Language the text should be translated into.
        @type target_language: str or unicode
        """
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
        """
        Change the translation status of a story title.

        @param document_id: MongoDB ID of document (_id)
        @type document_id: int
        @param language: Language the text should be translated into.
        @type language: str or unicode
        @param new_status: New translation status.
        @type new_status: str or unicode
        """
        self.mdb_client.update_document(
            self.story_collection,
            document_id,
            updates={
                "titles.{}.translation_status".format(language): new_status
            }
        )

    def _add_translated_story_title(self, document_id, language,
                                    translated_title):
        """
        Add a new translation of a story title.

        @param document_id: MongoDB ID of document (_id)
        @type document_id: int
        @param language: Language the text should be translated into.
        @type language: str or unicode
        @param translated_title: Title... in another language??
        @type translated_title: str or unicode
        """
        self.mdb_client.update_document(
            self.story_collection,
            document_id,
            updates={
                "titles.{}.title".format(language): translated_title
            }
        )
