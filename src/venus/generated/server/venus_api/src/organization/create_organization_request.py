import typing

import pydantic

from ..commons.organization_id import OrganizationId


class CreateOrganizationRequest(pydantic.BaseModel):
    organization_id: OrganizationId = pydantic.Field(alias="organizationId")
    artifact_read_requires_token: typing.Optional[bool] = pydantic.Field(
        alias="artifactReadRequiresToken"
    )

    class Config:
        allow_population_by_field_name = True
