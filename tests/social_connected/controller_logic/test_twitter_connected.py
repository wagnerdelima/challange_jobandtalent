from unittest.mock import patch, MagicMock

from parameterized import parameterized

from django.test import TestCase

from social_connected.controller_logic.twitter_connected import (
    TwitterConnected,
)


class TestTwitterConnected(TestCase):
    def setUp(self) -> None:
        self.twitter_connected = TwitterConnected('dev1', 'dev2')

    def relationship_fixture(
        self, following: bool = True, followed_by: bool = True
    ):
        return {
            'relationship': {
                'source': {
                    'screen_name': 'dev1',
                    'following': following,
                    'followed_by': followed_by,
                },
                'target': {
                    'screen_name': 'dev2',
                    'following': following,
                    'followed_by': followed_by,
                },
            }
        }

    def test_read_relationship_connected_success(self):
        with patch(
            'social_connected.controller_logic.twitter_connected.requests'
        ) as mocker:
            status = 200
            mock_request = MagicMock()
            mock_request.status_code = status
            mock_request.json.return_value = self.relationship_fixture()
            mocker.get.return_value = mock_request

            with patch.object(
                self.twitter_connected, '_check_for_user_errors'
            ) as mock_errors:
                mock_errors.return_value = [], status

                response = self.twitter_connected.connected()
            self.assertEqual(({'connected': True}, status), response)

    def test_read_relationship_unconnected_fail(self):
        with patch(
            'social_connected.controller_logic.twitter_connected.requests'
        ) as mocker:
            status = 200
            mock_request = MagicMock()
            mock_request.status_code = status
            mock_request.json.return_value = self.relationship_fixture(
                following=False
            )
            mocker.get.return_value = mock_request

            with patch.object(
                self.twitter_connected, '_check_for_user_errors'
            ) as mock_errors:
                mock_errors.return_value = [], status

                response = self.twitter_connected.connected()
            self.assertEqual(({'connected': False}, status), response)

    def test_read_relationship_one_user_exist_only_fail(self):
        with patch(
            'social_connected.controller_logic.twitter_connected.requests'
        ) as mocker:
            status = 200
            mock_request = MagicMock()
            mock_request.status_code = status
            mock_request.json.return_value = {
                'errors': [{'code': 50, 'message': 'User not found.'}]
            }
            mocker.get.return_value = mock_request

            with patch.object(
                self.twitter_connected, '_check_for_user_errors'
            ) as mock_errors:
                error = ['dev1 is not a valid user in twitter']
                mock_errors.return_value = error, status

                response = self.twitter_connected.connected()
            self.assertEqual(({'errors': error}, status), response)

    def test_user_exist_success(self):
        with patch(
            'social_connected.controller_logic.twitter_connected.requests'
        ) as mocker:
            status = 200
            mock_request = MagicMock()
            mock_request.status_code = status
            mock_request.json.return_value = [
                {'screen_name': 'dev1'},
                {'screen_name': 'dev2'},
            ]
            mocker.get.return_value = mock_request

            response = self.twitter_connected._check_for_user_errors(
                headers={'Authorization': 'Token'}
            )

            self.assertEqual(
                ([], status), response,
            )

    @parameterized.expand([('dev1',), ('dev2',)])
    def test_one_user_exist_only_fail(self, developer_login):
        with patch(
            'social_connected.controller_logic.twitter_connected.requests'
        ) as mocker:
            status = 200
            mock_request = MagicMock()
            mock_request.status_code = status
            mock_request.json.return_value = [
                {'screen_name': developer_login},
            ]
            mocker.get.return_value = mock_request

            response = self.twitter_connected._check_for_user_errors(
                headers={'Authorization': 'Token'}
            )

            if developer_login == 'dev1':
                self.assertEqual(
                    (['dev2 is not a valid user in twitter'], status),
                    response,
                )
            else:
                self.assertEqual(
                    (['dev1 is not a valid user in twitter'], status),
                    response,
                )

    def test_user_exist_fail(self):
        with patch(
            'social_connected.controller_logic.twitter_connected.requests'
        ) as mocker:
            status = 404
            mock_request = MagicMock()
            mock_request.status_code = status
            mock_request.json.return_value = {
                'errors': [
                    {
                        'code': 17,
                        'message': 'No user matches for specified terms.',
                    }
                ]
            }
            mocker.get.return_value = mock_request

            response = self.twitter_connected._check_for_user_errors(
                headers={'Authorization': 'Token'}
            )

            self.assertEqual(
                (
                    [
                        'dev1 is not a valid user in twitter',
                        'dev2 is not a valid user in twitter',
                    ],
                    status,
                ),
                response,
            )

    def test_request_params(self):
        params = self.twitter_connected._request_params()

        self.assertEqual(
            {'source_screen_name': 'dev1', 'target_screen_name': 'dev2',},
            params,
        )
