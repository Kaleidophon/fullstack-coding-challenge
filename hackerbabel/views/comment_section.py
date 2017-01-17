# -*- coding: utf-8 -*-

"""
View for a commentary section concerning a news article.
"""

# EXT
from flask import render_template, Blueprint

# PROJECT
from hackerbabel.cache import cache
from hackerbabel.src.helpers import get_story
from hackerbabel.config import REFRESH_INTERVAL

# CONST
COMMENT_SECTION = Blueprint(
    'comment_section', __name__,
    url_prefix='/<story_id>'
)


@cache.cached(timeout=REFRESH_INTERVAL)
@COMMENT_SECTION.route('/comments')
def comment_section(story_id):
    """
    View of a comment section under a news article.
    """
    return render_template(
        "comment_section.html",
        story_id=story_id,
        story=get_story(int(story_id))
    )
