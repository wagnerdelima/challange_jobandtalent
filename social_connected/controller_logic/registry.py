from typing import Dict, List, Any

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from social_connected.models import SocialRegistry, CommonOrganizations


class Registry:
    def __init__(self, source_dev: str = '', target_dev: str = '') -> None:
        self.source_developer: str = source_dev
        self.target_developer: str = target_dev

    def retrieve_registries(self) -> List[Dict[str, Any]]:
        """
        Retrieve history of developers connections.
        Connections will be retrieved by ascending order.
        """
        try:
            registries = SocialRegistry.objects.filter(
                source_developer=self.source_developer,
                target_developer=self.target_developer,
            )
            first_registry = registries.first()
            # joins all organizations linked to both
            # developers by the registry id.
            organizations = CommonOrganizations.objects.filter(
                social_registry=first_registry
            ).prefetch_related('social_registry')

            response = []
            for index, registry in enumerate(registries):
                orgs = []
                # matches orgs and registries by transaction id.
                # this way we can set an organizations key only for those
                # records with connections.
                # also we keep an ascending history of all records.
                for organization in organizations:
                    if registry.transaction_id == organization.transaction_id:
                        orgs.append(organization.organization)
                response.append(
                    {
                        'registered_at': registry.registered_at,
                        'connected': registry.connected,
                    }
                )
                # avoid adding organization to the
                # response if connection is not true.
                if orgs:
                    response[index]['organizations'] = orgs

        except Exception as exception:
            return {'errors': [str(exception)]}, HTTP_500_INTERNAL_SERVER_ERROR
        return response, HTTP_200_OK
