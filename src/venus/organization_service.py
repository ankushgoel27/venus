import logging

from fastapi import Depends

import venus.generated.server.resources.organization as fern

from venus.auth.auth0_client import Auth0Client
from venus.generated.server.resources.commons import UnauthorizedError
from venus.generated.server.resources.organization import AddUserToOrgRequest
from venus.generated.server.resources.organization import Organization
from venus.generated.server.security import ApiAuth
from venus.global_dependencies import get_auth0
from venus.global_dependencies import get_nursery_client
from venus.nursery.client import NurseryApiClient
from venus.nursery.resources import CreateOwnerRequest
from venus.nursery.resources.owner.types.update_owner_request import (
    UpdateOwnerRequest,
)
from venus.nursery_owner_data import NurseryOrgData
from venus.nursery_owner_data import read_nursery_org_data
from venus.utils import get_nursery_owner
from venus.utils import get_owner
from venus.utils import get_owner_id_from_token
from venus.utils import is_member_of_org


logger = logging.getLogger(__name__)


class OrganizationsService(fern.AbstractOrganizationService):
    def create(
        self,
        *,
        body: fern.CreateOrganizationRequest,
        auth: ApiAuth,
        auth0_client: Auth0Client = Depends(get_auth0),
        nursery_client: NurseryApiClient = Depends(get_nursery_client),
    ) -> None:
        user_id = auth0_client.get_user_id_from_token(auth.token)
        auth0_org_id = auth0_client.get().create_organization(
            org_id=body.organization_id.get_as_str()
        )
        nursery_org_data = NurseryOrgData(auth0_id=auth0_org_id)
        nursery_client.owner.create(
            body=CreateOwnerRequest(
                owner_id=body.organization_id.get_as_str(),
                data=nursery_org_data,
            )
        )
        auth0_client.get().add_user_to_org(
            user_id=user_id, org_id=auth0_org_id
        )

    def update(
        self,
        org_id: str,
        body: fern.UpdateOrganizationRequest,
        nursery_client: NurseryApiClient = Depends(get_nursery_client),
    ) -> None:
        get_owner_response = nursery_client.owner.get(owner_id=org_id)
        if not get_owner_response.ok:
            raise Exception(
                "Encountered error while retrieving org",
                get_owner_response.error,
            )
        org_data = read_nursery_org_data(get_owner_response.body.data)
        org_data.artifact_read_requires_token = (
            body.artifact_read_requires_token
        )
        owner_update_response = nursery_client.owner.update(
            owner_id=org_id,
            body=UpdateOwnerRequest(data=org_data),
        )
        if not owner_update_response.ok:
            raise Exception(
                "Encountered error while updating org",
                owner_update_response.error,
            )

    def is_member(
        self,
        *,
        organization_id: str,
        auth: ApiAuth,
        auth0_client: Auth0Client = Depends(get_auth0),
        nursery_client: NurseryApiClient = Depends(get_nursery_client),
    ) -> bool:
        return is_member_of_org(
            organization_id, auth, auth0_client, nursery_client
        )

    def get(
        self,
        org_id: str,
        nursery_client: NurseryApiClient = Depends(get_nursery_client),
    ) -> fern.Organization:
        return get_owner(owner_id=org_id, nursery_client=nursery_client)

    def get_my_organization_from_scoped_token(
        self,
        *,
        auth: ApiAuth,
        nursery_client: NurseryApiClient = Depends(get_nursery_client),
    ) -> Organization:
        owner_id = get_owner_id_from_token(
            auth=auth, nursery_client=nursery_client
        )
        logging.debug(f"Token has owner id {owner_id}")
        return get_owner(owner_id=owner_id, nursery_client=nursery_client)

    def add_user(
        self,
        *,
        body: AddUserToOrgRequest,
        auth: ApiAuth,
        auth0_client: Auth0Client = Depends(get_auth0),
        nursery_client: NurseryApiClient = Depends(get_nursery_client),
    ) -> None:
        user_id = auth0_client.get_user_id_from_token(auth.token)
        user_org_ids = auth0_client.get().get_orgs_for_user(user_id=user_id)
        if body.org_id.get_as_str() not in user_org_ids:
            raise UnauthorizedError()
        nursery_owner_data = get_nursery_owner(
            owner_id=body.org_id.get_as_str(), nursery_client=nursery_client
        )
        auth0_client.get().add_user_to_org(
            user_id=user_id, org_id=nursery_owner_data.auth0_id
        )
