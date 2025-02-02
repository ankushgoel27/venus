import typing

from typing import Dict
from uuid import uuid4

from venus.auth.auth0_client import AbstractAuth0Client
from venus.auth.auth0_client import AbstractVenusAuth0Client
from venus.auth.auth0_client import Auth0Org
from venus.generated.server.resources.organization import LightweightUser
from venus.generated.server.resources.user.types.user import User


org_id_to_auth0_id: Dict[str, str] = {}
auth0_org_id_to_members: Dict[str, typing.List[str]] = {}


class MockVenusAuth0Client(AbstractVenusAuth0Client):
    def create_organization(self, org_id: str) -> str:
        if org_id in org_id_to_auth0_id:
            raise Exception("Org already exists: ", org_id)
        auth0_id = str(uuid4())
        org_id_to_auth0_id[org_id] = auth0_id
        auth0_org_id_to_members[auth0_id] = []
        print(auth0_org_id_to_members)
        return auth0_id

    def get_user(self, *, user_id: str) -> User:
        return super().get_user(user_id=user_id)

    def get_raw_user(self, *, user_id: str) -> typing.Any:
        return None

    def get_orgs_for_user(self, *, user_id: str) -> typing.Set[Auth0Org]:
        return {
            Auth0Org(id="dummy-id", name="Dummy", display_name="Dummy")
            for org_id in self.get_org_ids_for_user(user_id=user_id)
        }

    def get_org_ids_for_user(self, *, user_id: str) -> typing.Set[str]:
        return set(auth0_org_id_to_members.keys())

    def add_user_to_org(self, *, user_id: str, org_id: str) -> None:
        if org_id in auth0_org_id_to_members:
            auth0_org_id_to_members[org_id].append(user_id)
        print(f"Org id {org_id} not in created orgs")

    def get_all_raw_users(self) -> typing.Generator[typing.Any, None, None]:
        yield None

    def get_users_for_org(
        self, *, org_id: str
    ) -> typing.List[LightweightUser]:
        result = []
        for member in auth0_org_id_to_members[org_id]:
            result.append(
                LightweightUser(
                    user_id=member, display_name="", picture_url=""
                )
            )
        return result

    def get_org(self, *, org_id: str) -> Auth0Org:
        return Auth0Org(id=org_id, name="Dummy", display_name="Dummy")


class MockAuth0Client(AbstractAuth0Client):
    def get(self) -> MockVenusAuth0Client:
        return MockVenusAuth0Client()

    def get_user_id_from_token(self, token: str) -> str:
        return "github|12303"
