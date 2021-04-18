from urllib.parse import urljoin
from typing import Dict, List, Union, Tuple
import concurrent.futures
import threading

import requests
from rest_framework.status import (
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_200_OK,
)

from django.conf import settings


class GithubConnected:
    """
    Provides logical mechanism for checking if two developers
    are connected in GitHub. Two people are considered connected
    if they have at least one organization in common.
    """

    def __init__(self, source_dev: str = '', target_dev: str = ''):
        self.source_dev: str = source_dev
        self.target_dev: str = target_dev

    def connected(
        self,
    ) -> Union[Tuple[Dict[str, List], int], Tuple[Dict[str, bool], int]]:
        """
        Check if two Github users are connected, that is,
        if both of them have at least one organization in common.

        :return: a dict if users are connected or a dict with a list of errors.
        """
        # Non-blocking requests to github urls of the two developers.
        # Returns a result of type generator.
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = executor.map(
                self._fetch_developer_organizations,
                (self.target_dev, self.source_dev),
            )

        first_response, first_status = next(results)
        second_response, second_status = next(results)

        def check_repeated_error(thread_response):
            """
            Prevent list of errors from having
            duplicate error messages.
            """
            error = thread_response.get('error')
            if error in errors:
                error = None

            if error:
                errors.append(error)

        errors = []
        status = HTTP_200_OK
        # Checks if any of the thread responses contain an error.
        # If at least one of the developers do not exist in github,
        # the response is an error.
        if 'error' in first_response:
            status = first_status
            check_repeated_error(first_response)
        if 'error' in second_response:
            status = second_status
            check_repeated_error(second_response)

        # if errors are found just stop execution and return
        if errors:
            return {'errors': errors}, status

        # a user may have more than one organization.
        # if at least one user's organization match another
        # user's organization they are GitHub connected.
        response = {'connected': False}
        organizations = []
        for first_result_org in first_response:
            if not response['connected']:
                # An organization can be identified
                # by its login. so we can check
                # If the login of one org is within all
                # the other orgs. If so, there is a connection
                if any(
                    (org := first_result_org.get('login'))
                    in second_result_org.values()
                    for second_result_org in second_response
                ):
                    organizations.append(org)
                    response = {
                        'connected': True,
                        'organizations': organizations
                    }

        return response, status

    def _get_session(self) -> requests.Session:
        """
        Create a request session for each thread. It's not clear
        from reading the requests library documentation, but reading this issue
        https://github.com/psf/requests/issues/2766 you will understand that
        each thread needs its own Session.

        :return: a request Session
        """
        thread_local = threading.local()
        if not hasattr(thread_local, 'session'):
            thread_local.session = requests.Session()
        return thread_local.session

    def _fetch_developer_organizations(
        self, developer_name: str
    ) -> Union[Tuple[List[Dict[str, str]], int], Tuple[Dict[str, str], int]]:
        """
        Fetch to the developer's organizations.

        :param developer_name: the username of develop in github.
        :return: a list of developer's organizations or a dict with
         an error if request is not successful.
        """
        headers = {'Accept': 'application/vnd.github.v3+json'}
        url: str = self._github_org_endpoint(developer_name)

        session = self._get_session()
        response = session.get(url, headers=headers)

        if response.status_code == HTTP_404_NOT_FOUND:
            return (
                {'error': f'{developer_name} is not a valid user in github',},
                HTTP_404_NOT_FOUND,
            )

        if response.status_code == HTTP_403_FORBIDDEN:
            return {'error': response.json()}, HTTP_403_FORBIDDEN

        return response.json(), HTTP_200_OK

    @staticmethod
    def _github_org_endpoint(developer_login: str) -> str:
        """
        Builds dynamic url based on developers username.

        :param developer_login: developer's login.
        :return: url
        """
        if not developer_login:
            raise ValueError('developer_login cannot be empty.')

        return urljoin(
            settings.GITHUB_API_BASE_URL, f'users/{developer_login}/orgs'
        )
