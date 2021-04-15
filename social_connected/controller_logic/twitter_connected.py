from urllib.parse import urljoin
from typing import Dict, List, Union

import requests

from rest_framework.status import HTTP_404_NOT_FOUND

from django.conf import settings


class TwitterConnected:
    """
    Provides logical mechanism for checking if two people are connected in Twitter.
    Two people are considered connected if they follow one another in twitter.
    """

    def __init__(self, source_dev: str = '', target_dev: str = '') -> None:
        self.source_dev: str = source_dev
        self.target_dev: str = target_dev

    def connected(self) -> Union[Dict[str, bool], Dict[str, List[str]]]:
        """
        Check if two twitter users are connected, that is, if both of them follow each other on twitter.
        :return: a dict stating if users are connected or a dict with errors.
        """
        headers = {'Authorization': settings.TWITTER_API_TOKEN}
        # checks if devs exist
        error_response = self._check_for_user_errors(headers)
        response = {'errors': error_response}
        # returns errors if one or more devs do not exist in twitter
        if not error_response:
            response = self._read_relationship(headers)

        return response

    def _check_for_user_errors(self, headers: Dict[str, str]):
        """
        Checks if the user's (developer in this case) response is successful or has errors.

        :param headers:
        :return: List of errors or an empty list if no errors request is successful.
        """
        response = self.__users_exist(headers)
        json_response = response.json()

        error_response = []
        if response.status_code == HTTP_404_NOT_FOUND:
            error_response.extend(
                [
                    f'{self.source_dev} is not a valid user in twitter',
                    f'{self.target_dev} is not a valid user in twitter',
                ]
            )
        # len 1 means that only one user is a valid user.
        # this way the users are not connected because one doesn't exist.
        elif len(json_response) == 1:
            name = json_response[0].get('screen_name')
            # the response is either one or both users.
            # this means that if only one user is in the response the missing user is invalid.
            if name == self.source_dev:
                name = self.target_dev
            else:
                name = self.source_dev

            error_response.append(f'{name} is not a valid user in twitter')

        return error_response

    def _read_relationship(self, headers: Dict[str, str]) -> Dict[str, bool]:
        """
        Check if two users follow each other.
        :param headers: Authorization headers
        :return: json with connected status.
        """
        # url to request for relationship in between two users in twitter
        friendship_url: str = urljoin(
            settings.TWITTER_API_BASE_URL, 'friendships/show.json'
        )
        request_params = self._request_params()
        response = requests.get(friendship_url, request_params, headers=headers)

        # raise exceptions if status above is 400 up to 600
        response.raise_for_status()

        json_response = response.json()

        source = json_response['relationship']['source']

        response = {'connected': False}
        if source['following'] and source['followed_by']:
            response['connected'] = True
        return response

    def __users_exist(self, headers: Dict[str, str]) -> requests.Response:
        """
        Fetch the user from Twitter.

        :return: A response from Twitter
        """
        # url that checks if user exists in twitter
        exist_url = urljoin(settings.TWITTER_API_BASE_URL, 'users/lookup.json')
        screen_name = ','.join([self.source_dev, self.target_dev])
        request_params = {'screen_name': screen_name}

        return requests.get(exist_url, request_params, headers=headers)

    def _request_params(self) -> Dict[str, str]:
        """
        Builds params for the GET request.
        """
        return {
            'source_screen_name': self.source_dev,
            'target_screen_name': self.target_dev,
        }
