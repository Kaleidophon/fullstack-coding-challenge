# -*- coding: utf-8 -*-

"""
Client used to access Hacker news
"""

# STD
import datetime
import json
import logging
import time

# EXT
from hackernews import HackerNews

# PROJECT
from hackerbabel.clients.client import Client
from hackerbabel.src.helpers import require_init

# CONST
NEW_NAMES = {
    u"kids": u"comments",
    u"by": u"author",
    u"type": u"article_type",
    u"time": u"date",
    u"title": u"titles"
}
DROPS = {u"descendants"}
LOGGER = logging.getLogger()


class HackerNewsClient(Client):
    formatting_functions = None
    target_langs = None

    @classmethod
    def initialize(cls, **init_kwargs):
        """
        Initialize the client.

        @param init_kwargs: Dictionary of init parameters, e.g. a config.
        @type init_kwargs: dict
        """
        cls.limit = init_kwargs.get("NUMBER_OF_STORIES", 10)
        cls.target_langs = init_kwargs.get("TARGET_LANGUAGES", ("PT",))
        cls.client = HackerNews()
        cls.formatting_functions = {
            u"comments": cls._collect_comments,
            u"date": cls._seconds_to_datestring,
            u"titles": cls._expand_title
        }
        cls.initialized = True

    @classmethod
    @require_init
    def get_top_stories(cls):
        """
        Return the stop stories of Hacker News as json (or future MongoDB
        document).

        @return: List of most recent top stories.
        @rtype: list
        """
        start_time = time.time()

        top_stories = [
            json.loads(getattr(cls._resolve_id(story_id), "raw"))
            for story_id in cls.client.top_stories(cls.limit)
        ]

        documents = [
            cls._jsonify_story(
                story, cls.formatting_functions, NEW_NAMES, DROPS
            )
            for story in top_stories
        ]

        end_time = time.time()
        minutes, seconds = divmod(round((end_time - start_time), 1), 60)

        LOGGER.info(
            "Received {} Hacker News stories in {} minute(s) {} second(s) with "
            "ids:\n{}\n".format(
                len(top_stories), minutes, seconds,
                ", ".join([str(top_story["id"]) for top_story in top_stories])
            )
        )

        return documents

    @staticmethod
    def _jsonify_story(story, formatting={}, rename={}, drop=set()):
        """
        Convert a story to a (MongoDB-ready) json.

        @param story: Top story from Hacker News
        @type story: dict
        @param formatting: Formatting function applied to the values of
        certain fields.
        @type formatting: dict
        @param rename: Dictionary of fields that should be renamed of form
        old name -> new name.
        @type rename: dict
        @param drop: Set of fields that will just be dropped.
        @type drop: set
        @return: MongoDB document
        @rtype: dict
        """
        document = story  # Semantic change from HN story to future MongoDB doc

        if not document.get("kids"):
            document["kids"] = []

        # Remove unwanted fields
        for field in drop:
            document.pop(field, None)

        # TODO: Is this the most efficient way to solve this problem?
        # Iterate through document / map?
        # Rename for readability
        for old_name in rename:
            if old_name in document:
                new_name = rename[old_name]
                document[new_name] = document[old_name]
                del document[old_name]

        # Format
        for field in formatting:
            if field in document:
                formatting_function = formatting[field]
                document[field] = formatting_function(document[field])

        return document

    @staticmethod
    def _seconds_to_datestring(seconds):
        """
        Convert seconds after 01.01.1980 to a date.

        @param seconds: Number of seconds.
        @type seconds: int
        @return: Date as string
        @rtype: str
        """
        date = datetime.datetime.utcfromtimestamp(seconds)
        return date.strftime("%d-%m-%Y, %H:%M")

    @classmethod
    def _expand_title(cls, title):
        """
        Convert title to dictionary, leaving room for data about the
        translation status and translated titles.

        @param title: Original title.
        @type title: str or unicode
        @return: Expanded title
        @rtype: dict
        """
        titles = {"EN": {
            "title": title,
            "translation_status": "done"
            }
        }

        for target_lang in cls.target_langs:
            titles.update({
                target_lang: {
                    "title": "###",  # Temporary title value
                    "translation_status": "not_requested"
                }
            })

        return titles

    @classmethod
    def _collect_comments(cls, comment_ids):
        """
        Collect comments from story and convert them to strings for MongoDB.

        @param comment_ids: List of comment IDs.
        @type comment_ids: list
        @return: List of converted comment IDs.
        @rtype: list
        """
        return [
            str(comment_id)
            for comment_id in comment_ids if comment_id is not None
        ]

    @classmethod
    def resolve_comment_ids(cls, story):
        """
        Recursively convert comment IDs to actual text.

        @param story: Story as json
        @type story: dict
        @return: Story with text comments
        @rtype: dict
        """
        # TODO: Make lookup into database if all these comments have already
        # been resolved for an older story / if number of comments for those
        # is the same
        # No comments, nothing to resolve / change
        if not story["comments"]:
            return story

        def _inner_resolve(comment_ids):
            comments = {}  # Comments of comment
            if not comment_ids:
                return comments
            for comment_id in comment_ids:
                comment = cls._resolve_id(comment_id)
                ccomment_ids = comment.kids
                comments[comment.text] = _inner_resolve(ccomment_ids)
                return comments

        resolved_comments = []
        for comment_id in story["comments"]:
            comment = cls._resolve_id(comment_id)
            ccomment_ids = comment.kids
            resolved_comments.append({
                comment.text: _inner_resolve(ccomment_ids)
            })

        story["comments"] = resolved_comments
        return story

    @classmethod
    def _resolve_id(cls, item_id):
        """
        Look up Hacker News object related to an ID.

        @param item_id: ID of item to be looked up.
        @return: Hacker News item
        @rtype: object
        """
        item_id = int(item_id)
        return cls.client.get_item(item_id)
