import posthog  # type: ignore

from venus.auth.auth0_client import AbstractAuth0Client
from venus.config import VenusConfig


class PosthogIdentityUpdater:
    def __init__(
        self, config: VenusConfig, auth0: AbstractAuth0Client
    ) -> None:
        self.auth0 = auth0
        if config.posthog_api_key is not None:
            posthog.project_api_key = config.posthog_api_key

    async def update_identities(self) -> None:
        user_generator = self.auth0.get().get_all_users()
        for user in user_generator:
            posthog.identify(user["user_id"], user)
