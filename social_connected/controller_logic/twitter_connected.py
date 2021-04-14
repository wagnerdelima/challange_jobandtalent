from urllib.parse import urljoin
from typing import Dict, List, Union

import requests

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
        error_response = self.__users_exist(headers)
        response = {'errors': error_response}
        # returns errors if one or more devs do not exist in twitter
        if not error_response:
            response = self.__read_relationship(headers)

        return response

    def __users_exist(self, headers: Dict[str, str]) -> List[str]:
        """
        Checks if a certain user (developer in this case) exists in twitter.
        Returns a True if user exists, otherwise returns False.

        :param headers: Authorizations headers.
        :return: a list of errors if the users do not exist, otherwise an empty list.
        """
        # url that checks if user exists in twitter
        exist_url = urljoin(settings.TWITTER_API_BASE_URL, 'users/lookup.json')
        screen_name = ','.join([self.source_dev, self.target_dev])
        request_params = {'screen_name': screen_name}

        response = requests.get(exist_url, request_params, headers=headers)
        json_response = response.json()

        error_response = []
        if 'errors' in json_response:
            error_response.extend(
                [
                    f'{self.source_dev} is not a valid user in twitter',
                    f'{self.target_dev} is not a valid user in twitter',
                ]
            )

        # len 1 means that only one user is a valid user
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

    def __read_relationship(self, headers: Dict[str, str]) -> Dict[str, bool]:
        """
        Check if two users follow each other.
        :param headers: Authorization headers
        :return: json with connected status.
        """
        # url to request for relationship in between two users in twitter
        friendship_url: str = urljoin(
            settings.TWITTER_API_BASE_URL, 'friendships/show.json'
        )
        request_params = self.__request_params()
        response = requests.get(friendship_url, request_params, headers=headers)

        # raise exceptions if status above is 400 up to 600
        response.raise_for_status()

        json_response = response.json()

        source = json_response['relationship']['source']

        response = {'connected': True}
        if not source['following'] and not source['followed_by']:
            response['connected'] = False
        return response

    def __request_params(self) -> Dict[str, str]:
        """
        Builds params for the GET request.
        """
        return {
            'source_screen_name': self.source_dev,
            'target_screen_name': self.target_dev,
        }
