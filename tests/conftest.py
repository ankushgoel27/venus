import os

import pytest
import requests

from venus.global_dependencies import config


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig) -> str:  # type: ignore
    return os.path.join(str(pytestconfig.rootdir), "compose-ete.yml")


def is_responsive(url: str):  # type: ignore
    try:
        response = requests.get(url)
        print(response)
        if response.status_code >= 200 and response.status_code < 300:
            return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def nursery_docker(docker_ip, docker_services):  # type: ignore
    print(config.nursery_origin + "/health")
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=1,
        check=lambda: is_responsive(config.nursery_origin + "/health"),
    )
