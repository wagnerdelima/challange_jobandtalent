from unittest.mock import patch

from django.contrib.auth.models import User

from rest_framework.test import APIClient, APITestCase


class TestSocialConnectedView(APITestCase):
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
