# -*- coding: utf-8 -*-

"""
View for a commentary section concerning a news article.
"""

# EXT
from flask import render_template, Blueprint

# CONST
COMMENT_SECTION = Blueprint(
    'comment_section', __name__,
    template_folder='../templates',
    static_folder='../static',
    url_prefix='/<story_id>'
)


@COMMENT_SECTION.route('/comments')
def comment_section(story_id):
    """
    View of a comment section under a news article.
    """
    return render_template("comment_section.html", story_id=story_id)
