# -*- coding: utf-8 -*-

"""
View for index / main page.
"""

# EXT
from flask import render_template, Blueprint

# PROJECT
from hackerbabel.src.helpers import get_stories

# CONST
INDEX = Blueprint('index', __name__)


@INDEX.route('/')
@INDEX.route('/index.html')
@INDEX.route('/start')
def index():
    """
    Main view
    """
    return render_template("index.html", stories=get_stories())
