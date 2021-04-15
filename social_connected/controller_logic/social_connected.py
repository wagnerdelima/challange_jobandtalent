from typing import Dict, Union, List

from social_connected.controller_logic.github_connected import GithubConnected
from social_connected.controller_logic.twitter_connected import TwitterConnected


class SocialConnected:
    def __init__(self, source_dev: str = '', target_dev: str = '') -> None:
        self.github = GithubConnected(source_dev, target_dev)
        self.twitter = TwitterConnected(source_dev, target_dev)

    def connected(self) -> Union[Dict[str, List[str]], Dict[str, bool]]:
        """
        Check if two developers are connected in both GitHub and Twitter.
        The condition to be connected are:
            1. The two developers have accounts in GitHub and Twitter
            2. The developers follow each other on twitter
            3. The developers have to at least one organization
            in common in GitHub

        :return: a JSON if users are connected or a dict with a list of errors.
        """
        github_connected = self.github.connected()
        twitter_connected = self.twitter.connected()

        if 'errors' in github_connected or 'errors' in twitter_connected:
            return {
                'errors': [
                    github_connected.get('errors', [])
                    + twitter_connected.get('errors', [])
                ]
            }

        connected = {}
        if github_connected['connected'] and twitter_connected['connected']:
            connected['connected'] = True
        else:
            connected['connected'] = False

        return connected
