import logging

import venus.generated.server.resources.commons as fern_commons

from venus.auth.auth0_client import Auth0Client
from venus.generated.server.resources.commons.errors import UnauthorizedError
from venus.generated.server.resources.organization.types.organization import (
    Organization,
)
from venus.generated.server.security import ApiAuth
from venus.nursery.client import NurseryApiClient
from venus.nursery.resources.token.types.get_token_metadata_request import (
    GetTokenMetadataRequest,
)
from venus.nursery_owner_data import NurseryOrgData
from venus.nursery_owner_data import read_nursery_org_data


def is_member_of_org(
    organization_id: str,
    auth: ApiAuth,
    auth0_client: Auth0Client,
    nursery_client: NurseryApiClient,
) -> bool:
    if auth.token.startswith("fern"):
        print(auth.token, "Token starts with fern, it is a nursery token")
        try:
            owner_id = get_owner_id_from_token(
                auth=auth, nursery_client=nursery_client
            )
            return owner_id == organization_id
        except UnauthorizedError:
            return False
    elif is_valid_jwt(auth.token, auth0_client):
        print(auth.token, "Token is a valid JWT, it is a user token")
        user_id = auth0_client.get_user_id_from_token(auth.token)
        nursery_owner = get_nursery_owner(
            owner_id=organization_id, nursery_client=nursery_client
        )
        org_ids = auth0_client.get().get_orgs_for_user(user_id=user_id)
        return nursery_owner.auth0_id in org_ids
    else:  # assume it is a legacy unprefixed nursery token
        print(
            auth.token,
            "Token neither starts with Fern nor is a JWT."
            "It is a nursery token.",
        )
        try:
            owner_id = get_owner_id_from_token(
                auth=auth, nursery_client=nursery_client
            )
            return owner_id == organization_id
        except UnauthorizedError:
            return False


def is_valid_jwt(token: str, auth0_client: Auth0Client) -> bool:
    try:
        auth0_client.get_user_id_from_token(token=token)
        return True
    except Exception:
        return False


def get_owner_id_from_token(
    *,
    auth: ApiAuth,
    nursery_client: NurseryApiClient,
) -> str:
    get_token_metadata_response = nursery_client.token.get_token_metadata(
        body=GetTokenMetadataRequest(token=auth.token)
    )
    if not get_token_metadata_response.ok:
        raise fern_commons.UnauthorizedError()
    token_status = get_token_metadata_response.body.status.get_as_union()
    if token_status.type == "expired" or token_status.type == "revoked":
        raise fern_commons.UnauthorizedError()
    owner_id = get_token_metadata_response.body.owner_id
    return owner_id


def get_owner(
    *, owner_id: str, nursery_client: NurseryApiClient
) -> Organization:
    org_data = get_nursery_owner(
        owner_id=owner_id, nursery_client=nursery_client
    )
    return Organization(
        organization_id=fern_commons.OrganizationId.from_str(owner_id),
        artifact_read_requires_token=org_data.artifact_read_requires_token,
    )


def get_nursery_owner(
    *, owner_id: str, nursery_client: NurseryApiClient
) -> NurseryOrgData:
    logging.debug(f"Getting owner with id {owner_id}")
    get_owner_response = nursery_client.owner.get(owner_id=owner_id)
    if not get_owner_response.ok:
        raise Exception(
            f"Error while retrieving owner from nursery with id={owner_id}",
            get_owner_response.error,
        )
    return read_nursery_org_data(get_owner_response.body.data)
