# -*- coding: utf-8 -*-

"""
View for the dashboard. The dashboard gives the user information about the
translation status of the news stories' headlines.
"""

# EXT
from flask import render_template, Blueprint

# CONST
DASHBOARD = Blueprint(
    'dashboard', __name__,
    template_folder='../templates',
    static_folder='../static'
)


@DASHBOARD.route('/dashboard')
def dashboard():
    """
    Dashboard view.
    """
    return render_template("dashboard.html")
