# -*- coding: utf-8 -*-

"""
Tests for the UnbabelClient.
"""

# STD
import json
from time import sleep
from unittest import TestCase

# EXT
from nose.tools import ok_

# PROJECT
from hackerbabel.clients.unbabel_client import UnbabelClient
from hackerbabel.src.helpers import get_config_from_py_file
from hackerbabel.testing.configuration_tests import CONFIG_PATH


class UnbabelClientTestCase(TestCase):

	def __init__(self, *args, **kwargs):
		super(UnbabelClientTestCase, self).__init__()

	def runTest(self):
		self.test_translation()

	def test_translation(self):
		response1 = self.ub_client.make_translation_request(
			"Hello, this is a test.", "DE"
		)
		response_data1 = json.loads(response1.content)
		uid = response_data1["uid"]

		# Test if authentication is correct
		ok_(response1.status_code in (200, 201))

		# Test if requesting the translation status works
		response2 = self.ub_client.check_translation_status(uid)
		ok_(response2.status_code in (200, 201))
		response_data2 = json.loads(response2.content)
		translation_status = response_data2["status"]
		# Depending on the current speed on Unbabel's side
		ok_(translation_status in ("new", "accepted", "translating"))

		# [Putting this all in comments because you don't want to have unit
		# testing for all small project that is > 1 minute longer than
		# necessary ]
		# Making sure it worked out in the end (at least in Sandbox mode)
		# sleep(75)
		# response3 = self.ub_client.check_translation_status(uid)
		# ok_(response3.status_code in (200, 201))
		# response_data3 = json.loads(response3.content)
		# ok_(
		# 	response_data3["status"] == "completed",
		# 	" Translation status is '{}', 'completed' expected.".format(
		# 		response_data3["status"]
		# 	)
		# )

	def setUp(self):
		config = get_config_from_py_file(CONFIG_PATH)
		self.ub_client = UnbabelClient()
		self.ub_client.initialize(**config)
