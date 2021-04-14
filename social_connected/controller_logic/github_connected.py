from urllib.parse import urljoin
from typing import Dict, List, Union
import concurrent.futures
import threading

import requests
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from django.conf import settings


class GithubConnected:
    def __init__(self, source_dev: str = '', target_dev: str = '') -> None:
        self.source_dev: str = source_dev
        self.target_dev: str = target_dev

    def connected(self):
        """

        :return:
        """
        # Non-blocking requests to github urls of the two developers.
        # Returns a result of type generator.
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = executor.map(
                self.__fetch_developer_organizations, (self.target_dev, self.source_dev)
            )

        first_result = next(results)
        second_result = next(results)

        # if errors are found just stop execution and return
        errors = self.__check_errors(first_result, second_result)
        if errors:
            return {'errors': errors}

        # a user may have more than one organization.
        # if at least one user's organization match another
        # user's organization they are GitHub connected.
        response = {'connected': False}
        for first_result_org in first_result:
            if not response['connected']:
                # An organization can be identified by its login. so we can check
                # If the login of one org is within all the other orgs. If so, there is a connection
                if any(
                    first_result_org.get('login') in second_result_org.values()
                    for second_result_org in second_result
                ):
                    response = {'connected': True}

        return response

    def __check_errors(
        self, first_response: Dict, second_response: Dict
    ) -> List[Dict[str, str]]:
        """
        Check if API responses contain errors, if so put the errors within a list, unrepeated.

        :param first_response: the first API response for one developer.
        :param second_response: the second API response for another developer.
        :return: a list of errors
        """
        errors = []
        first_error = first_response.get('error')
        second_error = second_response.get('error')

        if 'error' in first_response and first_error not in errors:
            errors.append(first_error)
        if 'error' in second_response and second_error not in errors:
            errors.append(second_error)

        return errors

    def __get_session(self) -> requests.Session:
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

    def __fetch_developer_organizations(
        self, developer_name: str
    ) -> Union[List[Dict[str, str]], Dict[str, str]]:
        """
        Fetch to the developer's organizations.

        :param developer_name: the username of develop in github.
        :return: a list of developer's organizations or a dict with
         an error if request is not successful.
        """
        headers = {'Accept': 'application/vnd.github.v3+json'}
        url: str = self.__github_org_endpoint(developer_name)

        session = self.__get_session()
        response = session.get(url, headers=headers)

        if response.status_code == HTTP_404_NOT_FOUND:
            return {'error': f'{developer_name} is not a valid user in github'}

        if response.status_code == HTTP_403_FORBIDDEN:
            return {'error': response.json()}

        return response.json()

    def __github_org_endpoint(self, developer_login: str) -> str:
        """
        Builds dynamic url based on developers username.

        :param developer_login: developer's login.
        :return: url
        """
        return urljoin(settings.GITHUB_API_BASE_URL, f'users/{developer_login}/orgs')
