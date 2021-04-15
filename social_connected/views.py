from rest_framework import generics
from rest_framework.response import Response

from social_connected.controller_logic.social_connected import SocialConnected


class SocialConnectedView(generics.RetrieveAPIView):
    lookup_fields = ['source_dev', 'target_dev']

    def get(self, request, *args, **kwargs):
        """
        Check if two developers are connected in GitHub and Twitter.
        """
        url_params = {field: self.kwargs[field] for field in self.lookup_fields}
        social_connected = SocialConnected(**url_params)
        response, status = social_connected.connected()
        return Response(response, status=status)
