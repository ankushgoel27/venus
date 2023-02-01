import functools

from venus.auth.auth0_client import AbstractAuth0Client
from venus.auth.auth0_client import Auth0Client
from venus.config import VenusConfig
from venus.nursery.client import NurseryApiClient
from venus.posthog_identity_updater import PosthogIdentityUpdater


config = VenusConfig.create()


@functools.lru_cache()
def get_auth0() -> AbstractAuth0Client:
    return Auth0Client(config=config)


@functools.lru_cache()
def get_nursery_client() -> NurseryApiClient:
    return NurseryApiClient(origin=config.nursery_origin)


@functools.lru_cache()
def get_posthog_identity_updater() -> PosthogIdentityUpdater:
    return PosthogIdentityUpdater(config=config, auth0=get_auth0())
