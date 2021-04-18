from unittest.mock import patch, MagicMock

from django.test import TestCase

from social_connected.controller_logic.github_connected import GithubConnected


class TestGithubConnected(TestCase):
    def test_connect_success(self):
        dev1, dev2 = 'dev1', 'dev2'
        self.github_connected = GithubConnected(dev1, dev2)

        with patch(
            'social_connected.controller_logic.github_connected.requests'
        ) as mock_session:
            status = 200
            mock_request = MagicMock()
            mock_request.status_code = status
            mock_request.json.return_value = [{'login': 'organization'}]

            mock_session.Session().get.return_value = mock_request

            response = self.github_connected.connected()

            self.assertEqual((
                {'connected': True, 'organizations': ['organization']},
                status
            ), response)

    def test_connect_devs_do_not_exist_fail(self):
        dev1, dev2 = 'dev1', 'dev2'
        self.github_connected = GithubConnected(dev1, dev2)

        with patch(
            'social_connected.controller_logic.github_connected.requests'
        ) as mock_session:
            status = 404
            mock_request = MagicMock()
            mock_request.status_code = status

            mock_session.Session().get.return_value = mock_request

            response = self.github_connected.connected()

            self.assertEqual(
                (
                    {
                        'errors': [
                            'dev2 is not a valid user in github',
                            'dev1 is not a valid user in github',
                        ],
                    },
                    status,
                ),
                response,
            )

    def test_connect_403_forbidden_request(self):
        dev1, dev2 = 'dev1', 'dev2'
        self.github_connected = GithubConnected(dev1, dev2)

        with patch(
            'social_connected.controller_logic.github_connected.requests'
        ) as mock_session:
            status = 403
            mock_request = MagicMock()
            mock_request.status_code = status
            mock_request.json.return_value = {
                'error': f'{dev2} is not a valid user in github'
            }
            mock_session.Session().get.return_value = mock_request

            response = self.github_connected.connected()

            self.assertEqual(
                (
                    {
                        'errors': [
                            {'error': 'dev2 is not a valid user in github'}
                        ]
                    },
                    403,
                ),
                response,
            )

    def test_github_org_endpoint_success(self):
        developer_login = 'test_user'
        url = f'https://api.github.com/users/{developer_login}/orgs'
        built_url = GithubConnected._github_org_endpoint(developer_login)

        self.assertEqual(url, built_url)

    def test_github_org_endpoint_empty_login_exception(self):
        developer_login = ''
        with self.assertRaises(ValueError):
            GithubConnected._github_org_endpoint(developer_login)
