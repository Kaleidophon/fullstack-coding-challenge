# -*- coding: utf-8 -*-

"""
Run the app.
"""

# PROJECT
from hackerbabel import setup_app

if __name__ == "__main__":
    app = setup_app()
    app.run(use_reloader=False)
