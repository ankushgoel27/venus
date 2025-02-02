import os

from uuid import uuid4

import pytest

from venus.auth.auth0_client import Auth0Client
from venus.auth.auth0_client import sanitize_auth0_org_name
from venus.config import VenusConfig


VENUS_CONFIG = VenusConfig(
    auth0_client_id="8lyAgexpGrHZLhN2i1FNPSicjupACR1r",
    auth0_client_secret=os.getenv("VENUS_DEV_AUTH0_CLIENT_SECRET"),
    auth0_domain_name="fern-dev.us.auth0.com",
    auth0_mgmt_audience="https://fern-dev.us.auth0.com/api/v2/",
    auth0_venus_audience="venus-dev",
    nursery_origin="fake",
    posthog_api_key=None,
)


@pytest.mark.skip(reason="requires hitting auth0")
def test_auth0_create_org() -> None:
    auth0_client = Auth0Client(config=VENUS_CONFIG)
    venus_auth0_client = auth0_client.get()
    generated_org_name = "test_" + str(uuid4())
    venus_auth0_client.create_organization(org_id=generated_org_name)
    print("Created org " + generated_org_name)


@pytest.mark.skip(reason="requires hitting auth0")
def test_auth0_refresh_token() -> None:
    auth0_client = Auth0Client(config=VENUS_CONFIG)
    auth0_client._ensure_token_valid()


@pytest.mark.skip(reason="requires hitting auth0")
def test_auth0_get_user() -> None:
    token = "YOUR_TOKEN_HERE"
    auth0_client = Auth0Client(config=VENUS_CONFIG)
    user_id = auth0_client.get_user_id_from_token(token)
    print(f"user_id: {user_id}")
    user = auth0_client.get().get_user(user_id=user_id)
    print(user.json())


@pytest.mark.skip(reason="requires hitting auth0")
def test_auth0_add_user_to_org() -> None:
    org_id = "YOUR_ORG_ID_HERE"
    user_id = "YOUR_USER_ID_HERE"
    auth0_client = Auth0Client(config=VENUS_CONFIG)
    auth0_client.get().add_user_to_org(user_id=user_id, org_id=org_id)


@pytest.mark.skip(reason="requires hitting auth0")
def test_auth0_get_user_orgs() -> None:
    user_id = "github|10870189"
    auth0_client = Auth0Client(config=VENUS_CONFIG)
    orgs = auth0_client.get().get_orgs_for_user(user_id=user_id)
    print(orgs)


@pytest.mark.skip(reason="requires hitting auth0")
def test_auth0_get_all_users() -> None:
    auth0_client = Auth0Client(config=VENUS_CONFIG)
    user_generator = auth0_client.get().get_all_raw_users()
    for user in user_generator:
        print(user)


@pytest.mark.skip(reason="requires hitting auth0")
def test_auth0_get_all_users_for_org() -> None:
    auth0_client = Auth0Client(config=VENUS_CONFIG)
    org_id = "YOUR_ORG_ID_HERE"
    lightweight_users = auth0_client.get().get_users_for_org(org_id=org_id)
    for user in lightweight_users:
        print(user)


@pytest.mark.skip(reason="requires hitting auth0")
def test_auth0_get_org() -> None:
    auth0_client = Auth0Client(config=VENUS_CONFIG)
    org_id = "org_SyfYA7Lz8OtwFTSW"
    org = auth0_client.get().get_org(org_id=org_id)
    print(org)


def test_sanitize_auth0_org_name() -> None:
    assert sanitize_auth0_org_name("deep 123") == "deep-123"
    assert sanitize_auth0_org_name("deep-123") == "deep-123"
    assert sanitize_auth0_org_name("deep-123-*") == "deep-123"
    assert sanitize_auth0_org_name("-deep-123") == "deep-123"
