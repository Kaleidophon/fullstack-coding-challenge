# -*- coding: utf-8 -*-

"""
Simple daemon that gets regularly gets Hacker News' top news articles and
feeds them into MongoDB.
"""

# STD
from time import sleep
from threading import Thread

# PROJECT
from hackerbabel.clients.hackernews_client import HackerNewsClient
from hackerbabel.clients.mongodb_client import MongoDBClient


class SimpleDaemon(object):

	def __init__(self, daemon_func, daemon_args, interval):
		self.daemon_func = daemon_func
		self.daemon_args = daemon_args
		self.interval = interval

	def run(self):
		first = Thread(target=self.daemon_func, args=(self.daemon_args, ))
		first.daemon = True
		first.start()


class HackerNewsDaemon(SimpleDaemon):

	def __init__(self, interval):
		self.interval = interval
		self.hn_client = HackerNewsClient()
		self.mdb_client = MongoDBClient()

		super(HackerNewsDaemon, self).__init__(
			self.refresh_top_stories, tuple(), interval
		)

	def refresh_top_stories(self, *args):
		while True:
			for document in self.hn_client.get_top_stories():
				self.mdb_client.add_document(document, "articles")
			sleep(self.interval)
