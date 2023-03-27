from fastapi import Depends
from fern.nursery.client import FernNursery

from venus.auth.auth0_client import Auth0Client
from venus.generated.server.resources.commons.types.organization_id import (
    OrganizationId,
)
from venus.generated.server.resources.user.service.service import (
    AbstractUserService,
)
from venus.generated.server.resources.user.types.organizations_page import (
    OrganizationsPage,
)
from venus.generated.server.resources.user.types.user import User
from venus.generated.server.security import ApiAuth
from venus.global_dependencies import get_auth0
from venus.global_dependencies import get_nursery_client


class UserService(AbstractUserService):
    def __init__(
        self,
        auth0_client: Auth0Client = Depends(get_auth0),
        nursery_client: FernNursery = Depends(get_nursery_client),
    ) -> None:
        self.nursery_client = nursery_client
        self.auth0_client = auth0_client

    def get_myself(self, *, auth: ApiAuth) -> User:
        user_id = self.auth0_client.get_user_id_from_token(auth.token)
        return self.auth0_client.get().get_user(user_id=user_id)

    def get_my_organizations(
        self, *, page_id: int, auth: ApiAuth
    ) -> OrganizationsPage:
        user_id = self.auth0_client.get_user_id_from_token(auth.token)
        orgs = self.auth0_client.get().get_orgs_for_user(user_id=user_id)
        return OrganizationsPage(
            organizations=[
                # in the API, we use the org name as the identifier
                OrganizationId.from_str(org.name)
                for org in orgs
            ],
            next_page=None,
        )
