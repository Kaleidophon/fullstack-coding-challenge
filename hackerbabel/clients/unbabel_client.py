# -*- coding: utf-8 -*-

"""
Client used to access the Unbabel API (in sandbox mode, though)
"""

# STD
import json
import requests

# PROJECT
from hackerbabel.clients.client import Client
from hackerbabel.src.helpers import require_init


class UnbabelClient(Client):
    user = None
    mail = None
    api_secret = None
    api_uri = None

    @classmethod
    def initialize(cls, **init_kwargs):
        """
        Initialize the client.

        @param init_kwargs: Dictionary of init parameters, e.g. a config.
        @type init_kwargs: dict
        """
        cls.api_uri = init_kwargs.get("UNBABEL_API_URI")
        cls.user = init_kwargs.get("UNBABEL_API_USER")
        cls.mail = init_kwargs.get("UNBABEL_API_EMAIL")
        cls.api_secret = init_kwargs.get("UNBABEL_API_SECRET")
        api_info = {cls.user, cls.mail, cls.api_secret, cls.api_uri}

        if any([date is None for date in api_info]):
            raise ValueError(
                "Following data is missing to use the Unbabel API: {}".format(
                    " ,".join(
                        [date.__name__ for date in api_info if date is None]
                    )
                )
            )
        cls.initialized = True

    @classmethod
    @require_init
    def build_authorization_header(cls):
        """
        Build the authorization header for an API request.

        @return: Header with Api key and secret
        @rtype: dict
        """
        return {
            "Authorization": "ApiKey {user}:{secret}".format(
                user=cls.user, secret=cls.api_secret
            )
        }

    @classmethod
    @require_init
    def make_translation_request(cls, text, target_lang, **additional_data):
        """
        Request the API to translate a text.

        @param text: Text to be translated.
        @type text: str or unicode
        @param target_lang: Language the text should be translated into.
        @type target_lang: str or unicode
        @param additional_data: Additional data added to the request.
        @type additional_data: dict
        @return: Response to request
        @type: Response
        """
        authorization_header = cls.build_authorization_header()
        data = {
            "text": text, "target_language": target_lang.lower()
        }
        data.update(additional_data)
        return cls.make_api_request(
            "POST", cls.api_uri, data, authorization_header
        )

    @classmethod
    @require_init
    def check_translation_status(cls, uid):
        """
        Check translation status of a text given Unbabel API's job uid.

        @param uid: Unique Unbabel API job idea.
        @type uid: str or unicode
        @return: Response to request
        @type: Response
        """
        authorization_header = cls.build_authorization_header()
        return cls.make_api_request(
            "GET", headers=authorization_header, uri="{uri}{uid}/".format(
                uri=cls.api_uri, uid=uid
            )
        )

    @classmethod
    def make_api_request(cls, request_type, uri, data={}, headers={}, **kwargs):
        """
        Make an request to an API.

        @param request_type: Type of request, e.g. GET / PUT / POST / DELETE...
        @type request_type: str or unicode
        @param uri: URI of the API.
        @type uri: str or unicode
        @param data: Data sent with the API.
        @type data: dict
        @param headers: Request headers.
        @type headers: dict
        @param kwargs: Additional options for request.
        @type kwargs: dict
        @return: Response to request.
        @type: Response
        """
        headers.update({'Content-Type': 'application/json; charset=utf-8'})
        data = json.dumps(data)

        response = getattr(requests, request_type.lower())(
            uri, data=data, headers=headers, **kwargs
        )
        return response
