# -*- coding: utf-8 -*-

"""
View for index / main page.
"""

# EXT
from flask import render_template, Blueprint

# PROJECT
from hackerbabel.src.helpers import get_stories
from hackerbabel.cache import cache
from hackerbabel.config import (
    REFRESH_INTERVAL,
    SOURCE_LANGUAGE,
    STORY_COLLECTION
)

# CONST
INDEX = Blueprint('index', __name__)


@cache.cached(timeout=REFRESH_INTERVAL)
@INDEX.route('/')
@INDEX.route('/index.html')
@INDEX.route('/start')
def index():
    """
    Main view
    """
    return render_template(
        "index.html",
        stories=get_stories(STORY_COLLECTION),
        interval=REFRESH_INTERVAL,
        source=SOURCE_LANGUAGE
    )
