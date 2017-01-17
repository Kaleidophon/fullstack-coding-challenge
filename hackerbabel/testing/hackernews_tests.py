# -*- coding: utf-8 -*-

"""
Tests for the HackerNewsClient.
"""

# STD
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
EXPECTED_SPEED = 8


class HackerNewsClientTestCase(TestCase):
    """
    Test the HackerNews client.
    """
    def __init__(self, *args, **kwargs):
        super(HackerNewsClientTestCase, self).__init__()

    def runTest(self):
        self.check_immediacy()
        self.check_speed_and_consistency()

    def check_speed_and_consistency(self):
        """
        Check the speed of the client and if the story's format suits the
        schema.
        """
        start = time.time()
        stories = self.hn_client.get_top_stories()
        finish = time.time()

        speed = round((finish - start) / self.number_of_stories, 3)

        error_message = "Client took {} longer than expected ({} s / " \
            "story)".format(
            speed - EXPECTED_SPEED,
                EXPECTED_SPEED
        )
        ok_(speed < EXPECTED_SPEED, error_message)

        # Check if stories have the right format
        for story in stories:
            self.schema.validate(story)

    def check_immediacy(self):
        """
        Checks how recent the client's results are.
        """
        client_titles = [
            story["titles"]["EN"]["title"]
            for story in self.hn_client.get_top_stories()
        ]

        response = urllib2.urlopen(HACKER_NEWS_URI)
        hacker_news_html = response.read()
        hacker_news_soup = BeautifulSoup(hacker_news_html, 'html.parser')
        direct_titles = [
            tag.text for tag in
            list(hacker_news_soup.find_all('a', {"class": "storylink"}))
        ][:self.number_of_stories]

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
        # Allow error of one because headline can jump into / out of the TOP
        # n stories very quickly
        ok_(len(set(direct_titles) - set.intersection(set(client_titles))) < 2,
                error_msg)

    def setUp(self):
        config = get_config_from_py_file(CONFIG_PATH)
        self.number_of_stories = config.get("NUMBER_OF_STORIES", 10)
        self.hn_client = HackerNewsClient()
        self.hn_client.initialize(**config)
        self.schema = ArticleSchema()
