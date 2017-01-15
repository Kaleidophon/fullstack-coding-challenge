# -*- coding: utf-8 -*-

"""
View for index / main page.
"""

# EXT
from flask import render_template, Blueprint

# PROJECT
from hackerbabel.clients.mongodb_client import MongoDBClient

# CONST
INDEX = Blueprint('index', __name__)


@INDEX.route('/')
@INDEX.route('/index.html')
@INDEX.route('/start')
def index():
    """
    Main view
    """
    mdb_client = MongoDBClient()
    stories = mdb_client.get_newest_documents("articles", 10)
    return render_template("index.html", stories=stories)
