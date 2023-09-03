import logging

from fern.nursery.client import FernNursery

import venus.generated.server.resources.commons as fern_commons

from venus.auth.auth0_client import Auth0Client
from venus.generated.server.resources.commons.errors import UnauthorizedError
from venus.generated.server.resources.organization.types.organization import (
    Organization,
)
from venus.generated.server.security import ApiAuth
from venus.nursery_owner_data import NurseryOrgData
from venus.nursery_owner_data import read_nursery_org_data


def is_member_of_org(
    organization_id: str,
    auth: ApiAuth,
    auth0_client: Auth0Client,
    nursery_client: FernNursery,
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
        users = auth0_client.get().get_users_for_org(
            org_id=nursery_owner.auth0_id
        )
        for user in users:
            if user.user_id == user_id:
                return True
        return False
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
    nursery_client: FernNursery,
) -> str:
    try:
        get_token_metadata_response = nursery_client.token.get_token_metadata(
            token=auth.token
        )
    except Exception:
        raise fern_commons.UnauthorizedError()

    token_status = get_token_metadata_response.status.get_as_union()
    if token_status.type == "expired" or token_status.type == "revoked":
        raise fern_commons.UnauthorizedError()
    owner_id = get_token_metadata_response.owner_id
    return owner_id


def get_owner(
    *,
    owner_id: str,
    nursery_client: FernNursery,
    auth0_client: Auth0Client,
) -> Organization:
    org_data = get_nursery_owner(
        owner_id=owner_id, nursery_client=nursery_client
    )
    lightweight_users = auth0_client.get().get_users_for_org(
        org_id=org_data.auth0_id
    )
    auth0_org = auth0_client.get().get_org(org_id=org_data.auth0_id)
    return Organization(
        organization_id=fern_commons.OrganizationId.from_str(owner_id),
        artifact_read_requires_token=org_data.artifact_read_requires_token,
        users=lightweight_users,
        display_name=auth0_org.display_name,
    )


def get_nursery_owner(
    *, owner_id: str, nursery_client: FernNursery
) -> NurseryOrgData:
    logging.debug(f"Getting owner with id {owner_id}")
    try:
        get_owner_response = nursery_client.owner.get(owner_id=owner_id)
    except Exception as error:
        raise Exception(
            f"Error while retrieving owner from nursery with id={owner_id}",
            error,
        )

    return read_nursery_org_data(get_owner_response.data)
