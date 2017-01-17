# -*- coding: utf-8 -*-

"""
View for the dashboard. The dashboard gives the user information about the
translation status of the news stories' headlines.
"""

# EXT
from flask import render_template, Blueprint

# PROJECT
from cache import cache
from hackerbabel.src.helpers import get_stories
from hackerbabel.config import REFRESH_INTERVAL

# CONST
DASHBOARD = Blueprint('dashboard', __name__)


@cache.cached(timeout=REFRESH_INTERVAL/10.0)
@DASHBOARD.route('/dashboard')
def dashboard():
    """
    Dashboard view.
    """
    return render_template("dashboard.html", stories=get_stories())
