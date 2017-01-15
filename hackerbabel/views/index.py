# -*- coding: utf-8 -*-

"""
View for index / main page.
"""

# EXT
from flask import render_template, Blueprint

# CONST
INDEX = Blueprint('index', __name__)


@INDEX.route('/')
@INDEX.route('/index.html')
@INDEX.route('/start')
def index():
    """
    Main view
    """
    return render_template("index.html")
