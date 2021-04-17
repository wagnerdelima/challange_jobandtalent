from django.db import models
from django.utils import timezone


class SocialRegistry(models.Model):
    """
    Represents a connection between two developers.
    Contain a transaction id to match the exact connection with the Organization,
    in case the developers stop connecting in GitHub and Twitter
    and at a later stage they reconnect.
    """

    source_developer = models.CharField(
        max_length=80,
        blank=False,
        null=False,
        db_index=True,
        help_text='Username of source developer',
    )
    target_developer = models.CharField(
        max_length=80,
        blank=False,
        null=False,
        db_index=True,
        help_text='Username of target developer',
    )
    transaction_id = models.CharField(
        max_length=40,
        blank=False,
        null=False,
        unique=True,
        help_text='Matching transaction number.',
    )
    connected = models.BooleanField(default=False)

    registered_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Record of {self.source_developer} and {self.target_developer}'


class CommonOrganizations(models.Model):
    """
    Represents an Organization that is linekd to two developers.
    Contain a transaction id to match the exact connection with the SocialRegistry,
    in case the developers stop connecting in GitHub and Twitter
    and at a later stage they reconnect.
    """

    social_registry = models.ForeignKey(
        SocialRegistry, on_delete=models.CASCADE, null=False, blank=False,
    )
    transaction_id = models.CharField(
        max_length=40,
        blank=False,
        null=False,
        unique=True,
        help_text='Matching transaction number.',
    )
    organization = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        help_text='Name of organization common to both developers',
    )

    def __str__(self):
        return f'{self.organization}'
