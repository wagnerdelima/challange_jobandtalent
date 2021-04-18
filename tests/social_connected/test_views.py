from unittest.mock import patch

from django.contrib.auth.models import User

from rest_framework.test import APIClient, APITestCase


class TestViews(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User()
        self.user.save()

    def test_social_connected_endpoint_success(self):
        with patch(
                'social_connected.views.SocialConnected.connected'
        ) as mock_connection:
            connected = {'connected': True}
            mock_connection.return_value = connected, 200

            self.client.force_authenticate(user=self.user)
            response = self.client.get(
                '/connected/realtime/dev1/dev2', format='json',
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(connected, response.data)

    def test_social_registry_endpoint_success(self):
        with patch(
            'social_connected.views.Registry.retrieve_registries'
        ) as mock_connection:
            mock_response = [
                {
                    "registered_at": "2021-04-18T11:25:33.247119Z",
                    "connected": False
                },
                {
                    "registered_at": "2021-04-18T11:25:35.705718Z",
                    "connected": True,
                    'organizations': ['organization 1', 'organization 2']
                }
            ]
            mock_connection.return_value = mock_response, 200

            self.client.force_authenticate(user=self.user)
            response = self.client.get(
                '/connected/register/dev1/dev2', format='json',
            )

            self.assertEqual(200, response.status_code)
            self.assertEqual(mock_response, response.data)

    def test_social_connected_fail(self):
        with patch(
                'social_connected.views.SocialConnected.connected'
        ) as mock_connection:
            error = {
                'errors': [
                    'dev1 is not a valid user in github',
                    'dev2 is not a valid user in twitter',
                ]
            }
            mock_connection.return_value = error, 404

            self.client.force_authenticate(user=self.user)
            response = self.client.get(
                '/connected/realtime/dev1/dev2', format='json',
            )

            self.assertEqual(404, response.status_code)
            self.assertEqual(error, response.data)

    def test_social_registry_fail(self):
        with patch(
            'social_connected.views.Registry.retrieve_registries'
        ) as mock_connection:
            error = {
                'errors': [
                    'Internal Error',
                ]
            }
            mock_connection.return_value = error, 500

            self.client.force_authenticate(user=self.user)
            response = self.client.get(
                '/connected/register/dev1/dev2', format='json',
            )

            self.assertEqual(500, response.status_code)
            self.assertEqual(error, response.data)
