# -*- coding: utf-8 -*-

"""
Module defining simple daemons to get Hacker News on a regular basis and
translate them.
"""

# STD
from collections import namedtuple
import logging
import json
from time import sleep
from multiprocessing import Queue, Pool
from threading import Thread

# PROJECT
from hackerbabel.clients.hackernews_client import HackerNewsClient
from hackerbabel.clients.unbabel_client import UnbabelClient
from hackerbabel.clients.mongodb_client import MongoDBClient
from hackerbabel.config import NUMBER_OF_CORES
from hackerbabel.src.schema import ArticleSchema, CommentSchema, TitleSchema

# CONST
LOGGER = logging.getLogger(__name__)
JOB_QUEUE = Queue()


HackerBabelJob = namedtuple(
    "HackerBabelJob", [
        "job_type", "story_id", "target_collection", "info"
    ]
)


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
    def __init__(self, interval, source_lang, target_langs, story_collection,
                 title_collection, comment_collection):
        self.hn_client = HackerNewsClient()
        self.source_lang = source_lang
        self.target_langs = target_langs
        self.story_collection = story_collection
        self.title_collection = title_collection
        self.comment_collection = comment_collection
        self.queue = Queue()

        super(HackerNewsDaemon, self).__init__(
            self.refresh_top_stories, tuple(), interval
        )

    def add_story(self, document):
        story_id = document["id"]
        titles = document["titles"]

        # Sneak in IDs so they can be found later
        titles["id"] = story_id
        # Wrap in dict for MongoDB
        comments = {
            "id": story_id,
            "comments": document["comments"]
        }
        del document["titles"]
        del document["comments"]

        self.mdb_client.add_document(
            document, self.story_collection, schema=ArticleSchema()
        )
        self.mdb_client.add_document(
            titles, self.title_collection, schema=TitleSchema()
        )
        self.mdb_client.add_document(
            comments, self.comment_collection, schema=CommentSchema()
        )

    def refresh_top_stories(self, *args):
        """
        Refresh the current Hacker news stories.

        @param args: Argument of functions - in this case, none.
        @type args: tuple
        """
        global JOB_QUEUE

        while True:
            documents = self.hn_client.get_top_stories()
            ids = [
                (document["id"], document["titles"][self.source_lang]["title"])
                for document in documents
            ]

            # Prioritize job to resolve comments
            for story_id, title in ids:
                # Check if job has been done in the past
                if not self.mdb_client.find_document(
                        "id", story_id, self.comment_collection
                ):
                    # TODO: Check if number of comments is the same
                    job = HackerBabelJob(
                        job_type="resolve_comments",
                        story_id=story_id,
                        target_collection="comments",
                        info={}
                    )
                    JOB_QUEUE.put(job)

            # Add translation_jobs
            for story_id, title in ids:
                for target_lang in self.target_langs:
                    if not self.mdb_client.find_document(
                        "id", story_id, self.title_collection
                    ):
                        job = HackerBabelJob(
                            job_type="translate_titles",
                            story_id=story_id,
                            target_collection="titles",
                            info={
                                "title": title,
                                "target_language": target_lang
                            }
                        )
                        JOB_QUEUE.put(job)

            # Finally add stories
            for document in self.hn_client.get_top_stories():
                self.add_story(document)

            sleep(self.interval)


class MasterDaemon(SimpleDaemon):

    def __init__(self):
        super(MasterDaemon, self).__init__(
            self.distribute_work, tuple(), interval=40
        )

    def distribute_work(self, *args):
        global JOB_QUEUE

        while True:
            jobs = []
            while not JOB_QUEUE.empty() and len(jobs) > NUMBER_OF_CORES:
                jobs.append(JOB_QUEUE.get())

            LOGGER.info(u"Starting {} new jobs.".format(len(jobs)))
            pool = Pool(NUMBER_OF_CORES)
            pool.map_async(handle_job, jobs)

            sleep(self.interval)


def translate_title(job):
    """
    Translate a story title.

    @param job: Job with job details
    @type job: namedtuple
    """
    info = job.info
    title = info["title"]
    target_language = info["target_language"]
    story_id = job.story_id
    ub_client = UnbabelClient()

    logging.info(
        u"New process trying to translate '{title}' into {lang}".format(
            title=title, lang=target_language
        )
    )

    # Do initial request
    response = None
    status_code = 404
    while status_code != 201 and status_code != 200:
        response = ub_client.make_translation_request(
            title, target_language
        )
        status_code = response.status_code

    response_data = json.loads(response.content)
    uid = response_data["uid"]

    response_data = None
    status = "new"

    _change_story_translation_status(
        story_id, target_language, "pending", job.target_collection
    )

    # Check translation status
    while status != "completed":
        sleep(5)
        response = ub_client.check_translation_status(uid)
        response_data = json.loads(response.content)
        status = response_data["status"]

    translated_text = response_data["translatedText"]

    logging.info(
        u"Translation complete!\n'{title}' --({lang})--> '{transtitle}'".format(
            title=title, lang=target_language,
            transtitle=translated_text
        )
    )

    _change_story_translation_status(
        story_id, target_language, "done", job.target_collection
    )
    _add_translated_story_title(
        story_id, target_language, translated_text, job.target_collection
    )


def _change_story_translation_status(story_id, language, new_status,
                                     story_collection):
    """
    Change the translation status of a story title.

    @param story_id: Hacker News Story ID
    @type story_id: str or unicode
    @param language: Language the text should be translated into.
    @type language: str or unicode
    @param new_status: New translation status.
    @type new_status: str or unicode
    """
    mdb_client = MongoDBClient()
    mdb_client.update_document(
        story_collection,
        story_id,
        updates={
            "titles.{}.translation_status".format(language): new_status
        }
    )


def _add_translated_story_title(story_id, language, translated_title,
                                story_collection):
    """
    Add a new translation of a story title.

    @param story_id: Hacker News Story ID
    @type story_id: str or unicode
    @param language: Language the text should be translated into.
    @type language: str or unicode
    @param translated_title: Title... in another language??
    @type translated_title: str or unicode
    """
    mdb_client = MongoDBClient()
    mdb_client.update_document(
        story_collection,
        story_id,
        updates={
            "titles.{}.title".format(language): translated_title
        }
    )


def resolve_story_comments(job):
    """
    Resolve comment in a story.

    @param job: Job with job details
    @type job: namedtuple
    """
    story_id = job.story_id
    target_collection = job.target_collection
    mdb_client = MongoDBClient()
    hn_client = HackerNewsClient()

    logging.info(
        u"New process trying to resolve comments for story #{}".format(story_id)
    )

    comments = mdb_client.find_document("_id", story_id, target_collection)
    resolved_comments = hn_client.resolve_comment_ids(comments)

    mdb_client.update_document(
        target_collection, story_id, {"comments": resolved_comments}
    )

    logging.info(
        u"Finished resolving comments for story #{}".format(story_id)
    )


def handle_job(job):
    return JOB_ACTIONS[job.job_type](job)

JOB_ACTIONS = {
    "resolve_comments": resolve_story_comments,
    "translate_title": translate_title
}
