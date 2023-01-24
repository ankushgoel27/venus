import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from venus.generated.server.register import register
from venus.organization_service import OrganizationsService
from venus.registry_service import RegistryService
from venus.user_service import UserService


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


def start() -> None:
    """Launched with `poetry run start` at root level"""

    uvicorn.run(
        "venus.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )


if __name__ == "__main__":
    start()
