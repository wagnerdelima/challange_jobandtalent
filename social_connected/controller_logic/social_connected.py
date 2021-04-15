from typing import Dict, Union, List, Tuple

from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from social_connected.controller_logic.github_connected import GithubConnected
from social_connected.controller_logic.twitter_connected import TwitterConnected


class SocialConnected:
    def __init__(self, source_dev: str = '', target_dev: str = '') -> None:
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

        connected = {}
        if github_connected['connected'] and twitter_connected['connected']:
            connected['connected'] = True
        else:
            connected['connected'] = False

        return connected, 200
