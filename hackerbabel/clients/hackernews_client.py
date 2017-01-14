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
	u"time": u"date"
}
DROPS = {u"descendants", u"url", u"score"}


class HackerNewsClient(Client):
	formatting_functions = None

	@classmethod
	def initialize(cls, *init_args, **init_kwargs):
		cls.client = HackerNews()
		cls.formatting_functions = {
			u"comments": cls._resolve_comments,
			u"date": cls._seconds_to_datestring
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

		return document

	@staticmethod
	def _seconds_to_datestring(seconds):
		date = datetime.datetime.utcfromtimestamp(seconds)
		return date.strftime("%%d-%m-%Y, %H:%M")

	@classmethod
	def _resolve_comments(cls, comment_ids):
		return [cls._resolve_id(comment_id).text for comment_id in comment_ids]

	@classmethod
	def _resolve_id(cls, item_id):
		return cls.client.get_item(item_id)

if __name__ == "__main__":
	client = HackerNewsClient()
	client.initialize()
	for document in client.get_top_stories():
		print document


