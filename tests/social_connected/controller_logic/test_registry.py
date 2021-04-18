from itertools import cycle
from unittest.mock import patch

from model_bakery import baker

from django.test import TestCase

from social_connected.controller_logic.registry import Registry
from social_connected.models import CommonOrganizations, SocialRegistry


class TestRegistry(TestCase):
    def setUp(self) -> None:
        self.social_registry = baker.make(
            SocialRegistry,
            source_developer='dev1',
            target_developer='dev2',
            connected=True,
            _quantity=3,
        )
        self.organizations = baker.make(
            CommonOrganizations,
            social_registry=self.social_registry[0],
            organization=cycle(['org1', 'org2', 'org3']),
            transaction_id=cycle(
                [r.transaction_id for r in self.social_registry]
            ),
            _quantity=3,
        )
        self.registry = Registry('dev1', 'dev2')

    def test_retrieve_registries_success(self):
        response, status = self.registry.retrieve_registries()
        self.assertEqual(200, status)

        actual = [
            {
                'connected': True,
                'organizations': ['org1'],
            },
            {
                'connected': True,
                'organizations': ['org2'],
            },
            {
                'connected': True,
                'organizations': ['org3'],
            },
        ]

        for item in actual:
            self.assertTrue(any(item.items() <= r.items() for r in response))

    def test_retrieve_registries_exception_fail(self):
        with patch(
            'social_connected.controller_logic.registry.SocialRegistry.objects'
        ) as mock_query_set:
            mock_query_set.filter.side_effect = Exception(
                'Cannot find database'
            )

            response, status = self.registry.retrieve_registries()

            self.assertEqual(500, status)
            self.assertEqual({'errors': ['Cannot find database']}, response)
