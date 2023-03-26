# This file was auto-generated by Fern from our API Definition.

import typing

from backports.cached_property import cached_property

from ..resources.organization.client.client import OrganizationClient
from ..resources.registry.client.client import RegistryClient
from ..resources.user.client.client import UserClient


class FernVenusApi:
    def __init__(self, *, environment: str, token: typing.Optional[str] = None):
        self._environment = environment
        self._token = token

    @cached_property
    def organization(self) -> OrganizationClient:
        return OrganizationClient(environment=self._environment, token=self._token)

    @cached_property
    def registry(self) -> RegistryClient:
        return RegistryClient(environment=self._environment, token=self._token)

    @cached_property
    def user(self) -> UserClient:
        return UserClient(environment=self._environment, token=self._token)
