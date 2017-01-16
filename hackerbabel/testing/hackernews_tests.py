# -*- coding: utf-8 -*-

"""
Tests for the HackerNewsClient.
"""

# STD
import re
from unittest import TestCase
import urllib2
import time

# EXT
from bs4 import BeautifulSoup
from nose.tools import ok_

# PROJECT
from hackerbabel.clients.hackernews_client import HackerNewsClient
from hackerbabel.src.helpers import get_config_from_py_file
from hackerbabel.testing.configuration_tests import CONFIG_PATH
from hackerbabel.src.schema import ArticleSchema

# CONST
HACKER_NEWS_URI = "https://news.ycombinator.com/"
EXPECTED_TIME_PER_STORY = 1.5


class HackerNewsClientTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(HackerNewsClientTestCase, self).__init__()

    def runTest(self):
        self.check_immediacy()
        self.check_speed_and_consistency()

    def check_speed_and_consistency(self):
        start = time.time()
        stories = self.hn_client.get_top_stories()
        finish = time.time()

        speed = round((finish - start) / self.number_of_stories, 3)

        error_message = "Client took {} longer than expected ({} s / " \
            "story)".format(
                speed - EXPECTED_TIME_PER_STORY,
                EXPECTED_TIME_PER_STORY
        )
        ok_(speed < EXPECTED_TIME_PER_STORY, error_message)

        # Check if stories have the right format
        for story in stories:
            self.schema.validate(story)

    def check_immediacy(self):
        response = urllib2.urlopen(HACKER_NEWS_URI)
        hacker_news_html = response.read()
        hacker_news_soup = BeautifulSoup(hacker_news_html, 'html.parser')
        direct_titles = [
            tag.text for tag in
            list(hacker_news_soup.find_all('a', {"class": "storylink"}))
        ][:self.number_of_stories]

        client_titles = [
            story["titles"]["EN"]["title"]
            for story in self.hn_client.get_top_stories()
        ]

        # Check if both sources yield the same results
        # Telling error message in case of test failure
        error_msg = u"These news acquired directly differ from those of the " \
            u"client:\n\t{}".format(
                u"\n\t".join(
                    [pair[0] + "\t|\t" + pair[1]
                    for pair in zip(direct_titles, client_titles)
                    if pair[0] != pair[1]]
                )
            )
        ok_(direct_titles == client_titles, error_msg)

    def setUp(self):
        config = get_config_from_py_file(CONFIG_PATH)
        self.number_of_stories = config.get("NUMBER_OF_STORIES", 10)
        self.hn_client = HackerNewsClient()
        self.hn_client.initialize(**config)
        self.schema = ArticleSchema()
