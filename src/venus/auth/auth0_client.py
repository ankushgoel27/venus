import math
import traceback
import typing

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Optional

import jwt

from auth0.v3.authentication import GetToken
from auth0.v3.exceptions import Auth0Error
from auth0.v3.management import Auth0

from venus.config import VenusConfig
from venus.generated.server.resources.commons import UnauthorizedError
from venus.generated.server.resources.organization import LightweightUser
from venus.generated.server.resources.organization import (
    OrganizationAlreadyExistsError,
)
from venus.generated.server.resources.user import User


@dataclass
class Auth0Org:
    display_name: str


class AbstractVenusAuth0Client(ABC):
    @abstractmethod
    def create_organization(self, *, org_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_user(self, *, user_id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_raw_user(self, *, user_id: str) -> typing.Any:
        raise NotImplementedError

    @abstractmethod
    def get_orgs_for_user(self, *, user_id: str) -> typing.Set[str]:
        raise NotImplementedError

    @abstractmethod
    def add_user_to_org(self, *, user_id: str, org_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_all_raw_users(self) -> typing.Generator[typing.Any, None, None]:
        raise NotImplementedError

    @abstractmethod
    def get_users_for_org(
        self, *, org_id: str
    ) -> typing.List[LightweightUser]:
        raise NotImplementedError

    @abstractmethod
    def get_org(self, *, org_id: str) -> Auth0Org:
        raise NotImplementedError


class VenusAuth0Client(AbstractVenusAuth0Client):
    def __init__(self, auth0: Auth0):
        self.auth0 = auth0

    def create_organization(self, *, org_id: str) -> str:
        try:
            create_auth0_organization_response = (
                self.auth0.organizations.create_organization({"name": org_id})
            )
            print(
                "Created organization in auth0. Received response: ",
                create_auth0_organization_response,
            )
            return create_auth0_organization_response["id"]
        except Auth0Error as e:
            if e.status_code == 409:
                print(f"An organization with name {org_id} already exists")
                raise OrganizationAlreadyExistsError()
            raise e

    def get_user(self, *, user_id: str) -> User:
        get_user_response = self.auth0.users.get(user_id)
        return User(
            username=get_user_response["nickname"],
            user_id=get_user_response["user_id"],
            email=get_user_response["email"],
            created_at=get_user_response["created_at"],
        )

    def get_raw_user(self, *, user_id: str) -> typing.Any:
        return self.auth0.users.get(user_id)

    def get_orgs_for_user(self, *, user_id: str) -> typing.Set[str]:
        # TODO(dsinghvi): Fix, page through all orgs
        list_organizations_response = self.auth0.users.list_organizations(
            user_id, per_page=50
        )
        organization_ids = set()
        for organization in list_organizations_response["organizations"]:
            # we use the organization name as the identifier
            organization_ids.add(organization["name"])
        return organization_ids

    def add_user_to_org(self, *, user_id: str, org_id: str) -> None:
        self.auth0.organizations.create_organization_members(
            org_id, {"members": [user_id]}
        )

    def get_all_raw_users(self) -> typing.Generator[typing.Any, None, None]:
        users_list = self.auth0.users.list()
        total_users = users_list["total"]
        page_size = users_list["length"]
        for u in users_list["users"]:
            yield u
        del users_list
        for page in range(1, math.ceil(total_users / page_size)):
            for u in self.auth0.users.list(page=page)["users"]:
                yield u

    def get_users_for_org(
        self, *, org_id: str
    ) -> typing.List[LightweightUser]:
        users_list = self.auth0.organizations.all_organization_members(org_id)[
            "members"
        ]
        result: typing.List[LightweightUser] = []
        for user in users_list:
            result.append(
                LightweightUser(
                    user_id=user["user_id"],
                    picture_url=user["picture"],
                    display_name=user["name"],
                )
            )
        return result

    def get_org(self, *, org_id: str) -> Auth0Org:
        auth0_org = self.auth0.organizations.get_organization(org_id)
        return Auth0Org(display_name=auth0_org["display_name"])


class AbstractAuth0Client(ABC):
    @abstractmethod
    def get(self) -> AbstractVenusAuth0Client:
        raise NotImplementedError()

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> str:
        raise NotImplementedError()


class Auth0Client(AbstractAuth0Client):
    def __init__(self, config: VenusConfig):
        self.config = config
        self.mgmt_api_token: Optional[str] = None
        self.expiry_time: Optional[datetime] = None
        jwks_url = (
            f"https://{self.config.auth0_domain_name}/.well-known/jwks.json"
        )
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def get(self) -> VenusAuth0Client:
        self._ensure_token_valid()
        auth0 = Auth0(
            self.config.auth0_domain_name,
            self.mgmt_api_token,
        )
        return VenusAuth0Client(auth0)

    def get_user_id_from_token(self, token: str) -> str:
        try:
            expected_issuer = (
                self.config.auth0_domain_name
                if self.config.auth0_domain_name.startswith("http")
                else f"https://{self.config.auth0_domain_name}/"
            )
            print(expected_issuer)
            signing_key = self.jwks_client.get_signing_key_from_jwt(token).key
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                issuer=expected_issuer,
                audience=self.config.auth0_venus_audience,
            )
            return payload["sub"]
        except Exception:
            print(traceback.format_exc())
            raise UnauthorizedError()

    def _ensure_token_valid(self) -> None:
        if self.mgmt_api_token is None or self._is_expired():
            get_token = GetToken(self.config.auth0_domain_name)
            token = get_token.client_credentials(
                client_id=self.config.auth0_client_id,
                client_secret=self.config.auth0_client_secret,
                audience=self.config.auth0_mgmt_audience,
            )
            self.mgmt_api_token = token["access_token"]
            self.expiry_time = datetime.now() + timedelta(
                seconds=int(token["expires_in"]) - 1000
            )

    def _is_expired(self) -> bool:
        if self.expiry_time is not None:
            return datetime.now() > self.expiry_time
        return True
