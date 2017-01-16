# -*- coding: utf-8 -*-

"""
View for the dashboard. The dashboard gives the user information about the
translation status of the news stories' headlines.
"""

# EXT
from flask import render_template, Blueprint

# PROJECT
from hackerbabel.src.helpers import get_stories

# CONST
DASHBOARD = Blueprint('dashboard', __name__)


@DASHBOARD.route('/dashboard')
def dashboard():
    """
    Dashboard view.
    """
    return render_template("dashboard.html", stories=get_stories())
