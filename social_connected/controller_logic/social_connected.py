import uuid
from typing import Dict, Union, List, Tuple

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from django.db import transaction, IntegrityError

from social_connected.controller_logic.github_connected import GithubConnected
from social_connected.controller_logic.twitter_connected import (
    TwitterConnected,
)
from social_connected.models import SocialRegistry, CommonOrganizations


class SocialConnected:
    """
    Contain logic to create two socially connected devs from GitHub and Twitter
    """
    def __init__(self, source_dev: str = '', target_dev: str = '') -> None:
        self.source_developer: str = source_dev
        self.target_developer: str = target_dev

        self.github = GithubConnected(source_dev, target_dev)
        self.twitter = TwitterConnected(source_dev, target_dev)

    def connected(
        self,
    ) -> Union[Tuple[Dict[str, List], int], Tuple[Dict[str, bool], int]]:
        """
        Check if two developers are connected in both GitHub and Twitter.
        The condition to be connected are:
            1. The two developers have accounts in GitHub and Twitter
            2. The developers follow each other on twitter
            3. The developers have to at least one organization
            in common in GitHub

        :return: a positive connected status
        if users are connected or a dict with a list of errors.
        """
        github_connected, github_status = self.github.connected()
        twitter_connected, twitter_status = self.twitter.connected()

        if 'errors' in github_connected or 'errors' in twitter_connected:
            status = HTTP_400_BAD_REQUEST
            # if Twitter or GitHub returns a status code other than 200
            # there is an error and we should return the erroneous status.
            if github_status != HTTP_200_OK:
                status = github_status
            if twitter_status != HTTP_200_OK:
                status = twitter_status

            return (
                {
                    'errors': github_connected.get('errors', [])
                    + twitter_connected.get('errors', []),
                },
                status,
            )

        response = {}
        status = HTTP_200_OK
        try:
            # if both twitter and github responses are
            # connected than the devs are both connected
            if connected := (github_connected['connected'] and twitter_connected['connected']):
                # connected is True
                response['connected'] = connected
            else:
                # here connected is False
                response['connected'] = connected

            self.__save_response(connected, github_connected.get('organizations', []))

        except (IntegrityError, Exception) as exception:
            response = {'errors': [str(exception)]}
            status = HTTP_500_INTERNAL_SERVER_ERROR

        return response, status

    def __save_response(self, connected: bool, organizations: List[str]) -> None:
        """
        Save results. Results are saved only if there is no
        error from either GitHub or Twitter API.

        Organizations are only saved if devs are connected in both Twitter and GitHub.
        """
        with transaction.atomic():
            first_registry = SocialRegistry.objects.filter(
                source_developer=self.source_developer,
                target_developer=self.target_developer,
            ).first()

            transaction_id = uuid.uuid4()
            new_registry = SocialRegistry.objects.create(
                source_developer=self.source_developer,
                target_developer=self.target_developer,
                transaction_id=transaction_id,
                connected=connected
            )
            # we create organizations based on the id of the first dev1/dev2 endpoint call.
            registry = first_registry if first_registry else new_registry
            # only creates organizations if there devs are connected.
            if connected:
                orgs = [
                    CommonOrganizations(
                        social_registry=registry,
                        organization=org,
                        transaction_id=transaction_id,
                    ) for org in organizations
                ]

                CommonOrganizations.objects.bulk_create(orgs, ignore_conflicts=True)
