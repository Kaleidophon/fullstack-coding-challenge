# -*- coding: utf-8 -*-

"""
Client used to access Hacker news
"""

# STD
import datetime
import json

# EXT
from hackernews import HackerNews

# PROJECT
from hackerbabel.clients.client import Client
from hackerbabel.misc.helpers import require_init

# CONST
RENAMING = {
	u"kids": u"comments",
	u"by": u"author",
	u"type": u"article_type",
	u"time": u"date",
	u"title": u"titles"
}
DROPS = {u"descendants", u"url", u"score"}


class HackerNewsClient(Client):
	formatting_functions = None

	@classmethod
	def initialize(cls, **init_kwargs):
		cls.client = HackerNews()
		cls.formatting_functions = {
			u"comments": cls._resolve_comments,
			u"date": cls._seconds_to_datestring,
			u"titles": cls._expand_title
		}
		cls.initialized = True

	@classmethod
	@require_init
	def get_top_stories(cls, limit=10):
		top_stories = [
			json.loads(getattr(cls._resolve_id(story_id), "raw"))
			for story_id in cls.client.top_stories(limit)
		]

		documents = [
			cls._jsonify_story(
				story, cls.formatting_functions, RENAMING, DROPS
			)
			for story in top_stories
		]

		return documents

	@staticmethod
	def _jsonify_story(story, formatting={}, rename={}, drop=set()):
		document = story

		# Remove unwanted field
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

		document["translation_status"] = "not_requested"

		return document

	@staticmethod
	def _seconds_to_datestring(seconds):
		date = datetime.datetime.utcfromtimestamp(seconds)
		return date.strftime("%d-%m-%Y, %H:%M")

	@staticmethod
	def _expand_title(title):
		return {"EN": title}

	@classmethod
	def _resolve_comments(cls, comment_ids):
		def is_not_none(comment):
			if comment is not None:
				return True
			return False

		return filter(
			is_not_none,
			[cls._resolve_id(comment_id).text for comment_id in comment_ids]
		)

	@classmethod
	def _resolve_id(cls, item_id):
		return cls.client.get_item(item_id)

if __name__ == "__main__":
	from hackerbabel.clients.mongodb_client import MongoDBClient

	hn_client = HackerNewsClient()
	hn_client.initialize()

	mdb_client = MongoDBClient()
	mdb_client.initialize(host="127.0.0.1", database="hackerbabel_db")

	for document in hn_client.get_top_stories():
		print document
		mdb_client.add_document(document, "articles")


