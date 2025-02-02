import json

from uuid import uuid4

from fastapi.testclient import TestClient

from tests.mock_auth0_client import MockAuth0Client
from venus.global_dependencies import get_auth0
from venus.main import app

from .http_utils import assert_valid_status_code


client = TestClient(app)
app.dependency_overrides[get_auth0] = lambda: MockAuth0Client()


def test_generate_and_use_token(nursery_docker) -> None:  # type: ignore
    # create org
    org_id = str(uuid4())
    create_org_response = client.post(
        "/organizations/create",
        json={"organizationId": org_id, "artifactReadRequiresToken": True},
        headers={"Authorization": "Bearer dummy"},
    )
    assert_valid_status_code(create_org_response.status_code, "create_org")

    # generate token
    gen_token_response = client.post(
        "/registry/generate-tokens",
        json={"organizationId": org_id},
        headers={"Authorization": "Bearer dummy"},
    )
    print(gen_token_response.text)
    assert_valid_status_code(gen_token_response.status_code, "generate_token")

    # check token works
    npm_token = json.loads(gen_token_response.text)["npm"]["token"]
    print("npm token: ", npm_token)
    check_token_response = client.post(
        "/registry/check-permissions",
        json={
            "organizationId": org_id,
            "token": {
                "type": "npm",
                "token": npm_token,
            },
        },
    )
    assert check_token_response.status_code == 200

    my_org = client.post(
        "/organizations/myself",
        headers={"Authorization": f"Bearer {npm_token}"},
    )
    assert my_org.status_code == 200
