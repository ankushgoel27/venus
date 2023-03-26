from multiprocessing import Process
from typing import Generator
from uuid import uuid4

import pytest

from venus.generated.client.client.client import FernVenusApi
from venus.global_dependencies import get_auth0
from venus.global_dependencies import get_nursery_client
from venus.main import app
from venus.main import start_server

from .mock_auth0_client import MockAuth0Client


client = FernVenusApi(environment="http://localhost:8080")


app.dependency_overrides[get_auth0] = lambda: MockAuth0Client()


@pytest.fixture
def server() -> Generator[None, None, None]:
    """
    https://stackoverflow.com/a/57816608/4238485
    """
    proc = Process(target=start_server, args=(), daemon=True)
    proc.start()
    yield
    proc.kill()  # Cleanup after test


def test_create_and_update_org(nursery_docker):  # type: ignore
    # create_org
    org_id = str(uuid4())
    client.organization.create(organization_id=org_id)

    # get org from nursery
    get_owner_response = get_nursery_client().owner.get(owner_id=org_id)
    if get_owner_response.ok:
        print("get_owner_response", get_owner_response.body)
        assert (
            get_owner_response.body.data["artifactReadRequiresToken"] is False
        )
    else:
        raise Exception(
            "Failed to get owner from nursery", get_owner_response.error
        )

    # update_org
    client.organization.update(
        org_id=org_id, artifact_read_requires_token=True
    )

    # get org from nursery
    get_owner_response = get_nursery_client().owner.get(owner_id=org_id)
    if get_owner_response.ok:
        print("get_owner_response", get_owner_response.body)
        assert (
            get_owner_response.body.data["artifactReadRequiresToken"] is True
        )
    else:
        raise Exception(
            "Failed to get owner from nursery", get_owner_response.error
        )
