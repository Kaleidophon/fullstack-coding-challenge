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
        date = datetime.datetime.utcfromtimestamp(seconds)
        return date.strftime("%d-%m-%Y, %H:%M")

    @classmethod
    def _expand_title(cls, title):
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
        return [
            str(comment_id)
            for comment_id in comment_ids if comment_id is not None
        ]

    @classmethod
    def resolve_comment_ids(cls, story):

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
        item_id = int(item_id)
        return cls.client.get_item(item_id)
