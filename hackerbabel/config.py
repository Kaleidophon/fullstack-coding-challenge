PROPAGATE_EXCEPTIONS = True
LOGGER_FILE = "logs/hackerbabel.log"
LOGGER_LOGLEVEL = "DEBUG"
CONSOLE_LOGGING = True
DEBUG = True
TESTING = False
REFRESH_INTERVAL = 600
MONGODB_HOST = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_NAME = "hackerbabel_db"
NUMBER_OF_STORIES = 10
TARGET_LANGUAGES = ("DE", "PT")
UNBABEL_API_URI = "http://sandbox.unbabel.com/tapi/v2/translation/"
UNBABEL_API_USER = "Dennis.Ulmer"
UNBABEL_API_EMAIL = "Dennis.Ulmer@gmx.de"
# Putting sensible data in here isn't obviously best practice but will
# ( hopefully) do for this coding challenge
UNBABEL_API_SECRET = "e0b862dc3beb372b01712651e39aab3aa43578c8"

# TODO: Make this variable throughout the project
SOURCE_LANGUAGE = "EN"
STORY_COLLECTION = "articles"

# TODO: Add those
COMMENT_COLLECTION = "comments"
TITLE_COLLECTION = "titles"
