from unittest.mock import patch

from parameterized import parameterized

from django.test import TestCase

from social_connected.controller_logic.social_connected import SocialConnected


class TestSocialConnected(TestCase):
    def setUp(self) -> None:
        self.social_connected = SocialConnected('dev1', 'dev2')

    def github_error_fixture(self, dev_name: str):
        return {'errors': [f'{dev_name} is not a valid user in github']}

    def twitter_error_fixture(self, dev_name: str):
        return {'errors': [f'{dev_name} is not a valid user in twitter']}

    def twitter_and_github_error(self):
        return {
            'errors': [
                'dev2 is not a valid user in github',
                'dev1 is not a valid user in twitter',
            ]
        }

    def test_social_connected_success(self):
        with patch.object(self.social_connected, 'github') as mocker_github:
            with patch.object(
                self.social_connected, 'twitter'
            ) as mocker_twitter:
                connected = {'connected': True}
                status = 200
                mocker_twitter.connected.return_value = connected, status
                mocker_github.connected.return_value = connected, status

                response, status = self.social_connected.connected()
                self.assertEqual(200, status)
                self.assertEqual(connected, response)

    @parameterized.expand([(True, False), (False, True)])
    def test_social_connected_one_social_fail(self, github, twitter):
        with patch.object(self.social_connected, 'github') as mocker_github:
            with patch.object(
                self.social_connected, 'twitter'
            ) as mocker_twitter:
                status = 200
                mocker_twitter.connected.return_value = (
                    {'connected': twitter},
                    status,
                )
                mocker_github.connected.return_value = (
                    {'connected': github},
                    status,
                )

                response, status = self.social_connected.connected()
                self.assertEqual(200, status)
                self.assertEqual({'connected': False}, response)

    def test_social_connected_github_error_fail(self):
        with patch.object(self.social_connected, 'github') as mocker_github:
            with patch.object(
                self.social_connected, 'twitter'
            ) as mocker_twitter:
                mocker_twitter.connected.return_value = (
                    {'connected': True},
                    200,
                )

                error_message = self.github_error_fixture('dev1')
                mocker_github.connected.return_value = (error_message, 404)

                response, status = self.social_connected.connected()
                self.assertEqual(404, status)
                self.assertEqual(error_message, response)

    def test_social_connected_twitter_error_fail(self):
        with patch.object(self.social_connected, 'github') as mocker_github:
            with patch.object(
                self.social_connected, 'twitter'
            ) as mocker_twitter:
                error_message = self.twitter_error_fixture('dev2')
                mocker_twitter.connected.return_value = error_message, 404

                mocker_github.connected.return_value = {'connected': True}, 200

                response, status = self.social_connected.connected()
                self.assertEqual(404, status)
                self.assertEqual(error_message, response)

    def test_social_connected_error_fail(self):
        with patch.object(self.social_connected, 'github') as mocker_github:
            with patch.object(
                self.social_connected, 'twitter'
            ) as mocker_twitter:
                error_message = self.twitter_and_github_error()
                twitter_message = self.twitter_error_fixture('dev1')
                github_message = self.github_error_fixture('dev2')

                mocker_twitter.connected.return_value = twitter_message, 404
                mocker_github.connected.return_value = github_message, 404

                response, status = self.social_connected.connected()
                self.assertEqual(404, status)
                self.assertEqual(error_message, response)
