# -*- coding: utf-8 -*-

"""
JSON validation handler against defined schemas in subclasses.
"""

# STD
import logging

# EXT
from jsonschema import FormatChecker, ValidationError, Draft4Validator, validate

# CONST
LOGGER = logging.getLogger(__name__)


class Schema(object):
    """
    Base model and schema.

    JSON Schema Draft 4 is used. Documentation is under
    http://spacetelescope.github.io/understanding-json-schema/

    A business object is only allowed to be created if and only if validation
    against described schema is ok. Otherwise an error will be raised which
    should finally result in an (custom) error message.
    """
    def __init__(self, schema):
        self.schema = schema
        self.validator = Draft4Validator(self.schema)

    def validate(self, json_object):
        """
        Validate incoming json against model schema. An error will be raised
        if validation fails. Also, there is an option to do some extra
        validation defined in each specific schema to validate datatypes that
        JSON Schema doesn't support.

        @param json_object: json to validate
        @type json_object: dict
        @return: True if no error, else raise error (return messages for bulk)
        @rtype: list or bool
        """
        schema = self.schema

        try:
            validate(json_object, schema, format_checker=FormatChecker())

        except ValidationError as validation_error:
            LOGGER.error(
                u"Encountered error during validation: " +
                validation_error.message
            )
            raise validation_error


class ArticleSchema(Schema):
    """
    Special schema used to validate Hacker News stories.
    """
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "number"},
            "titles": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "translation_status": {
                        "type": "string"
                    }
                }
            },
            "date": {"type": "string"},
            "article_type": {"type": "string"},
            "author": {"type": "string"},
            "url": {"type": "string"},
            "text": {"type": "string"},
            "score": {"type": "number"},
            "comments": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
        },
        "required": [
            "id", "titles", "article_type", "author",
            "date", "score"
        ]
    }

    def __init__(self):
        super(ArticleSchema, self).__init__(self.schema)
