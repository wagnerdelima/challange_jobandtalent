from rest_framework import generics
from rest_framework.response import Response

from social_connected.controller_logic.twitter_connected import TwitterConnected


class SocialConnected(generics.RetrieveAPIView):
    lookup_fields = ['source_dev', 'target_dev']

    def get(self, request, *args, **kwargs):
        url_params = {field: self.kwargs[field] for field in self.lookup_fields}
        twitter_connected = TwitterConnected(**url_params)
        response = twitter_connected.connected()
        return Response(response)
