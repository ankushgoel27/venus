import asyncio

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from venus.generated.server.register import register
from venus.global_dependencies import get_posthog_identity_updater
from venus.organization_service import OrganizationsService
from venus.registry_service import RegistryService
from venus.user_service import UserService


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://www.app.buildwithfern.com",
        "https://app.buildwithfern.com",
        "https://www.app-dev.buildwithfern.com",
        "https://app-dev.buildwithfern.com",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register(
    app,
    organization=OrganizationsService(),
    registry=RegistryService(),
    user=UserService(),
)


@app.get("/health")
def health() -> None:
    pass


@app.on_event("startup")
async def app_startup() -> None:
    asyncio.create_task(get_posthog_identity_updater().update_identities())


def start_server() -> None:
    """Launched with `poetry run start` at root level"""

    uvicorn.run(
        "venus.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )


start = start_server

if __name__ == "__main__":
    start_server()
