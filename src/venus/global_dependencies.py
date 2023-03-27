import functools

from fern.nursery.client import FernNursery

from venus.auth.auth0_client import AbstractAuth0Client
from venus.auth.auth0_client import Auth0Client
from venus.config import VenusConfig
from venus.posthog_identity_updater import PosthogIdentityUpdater


config = VenusConfig.create()


@functools.lru_cache()
def get_auth0() -> AbstractAuth0Client:
    return Auth0Client(config=config)


@functools.lru_cache()
def get_nursery_client() -> FernNursery:
    return FernNursery(environment=config.nursery_origin)


@functools.lru_cache()
def get_posthog_identity_updater() -> PosthogIdentityUpdater:
    return PosthogIdentityUpdater(config=config, auth0=get_auth0())
