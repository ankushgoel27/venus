# This file was auto-generated by Fern from our API Definition.

# flake8: noqa
# fmt: off
# isort: skip_file

from __future__ import annotations

import typing

import pydantic
import typing_extensions

from ...commons.types.organization_id import OrganizationId


class OrganizationsPage(pydantic.BaseModel):
    organizations: typing.List[OrganizationId]
    next_page: typing.Optional[int] = pydantic.Field(alias="nextPage")

    class Validators:
        """
        Use this class to add validators to the Pydantic model.

            @OrganizationsPage.Validators.root
            def validate(values: OrganizationsPage.Partial) -> OrganizationsPage.Partial:
                ...

            @OrganizationsPage.Validators.field("organizations")
            def validate_organizations(v: typing.List[OrganizationId], values: OrganizationsPage.Partial) -> typing.List[OrganizationId]:
                ...

            @OrganizationsPage.Validators.field("next_page")
            def validate_next_page(v: typing.Optional[int], values: OrganizationsPage.Partial) -> typing.Optional[int]:
                ...
        """

        _validators: typing.ClassVar[
            typing.List[typing.Callable[[OrganizationsPage.Partial], OrganizationsPage.Partial]]
        ] = []
        _organizations_validators: typing.ClassVar[
            typing.List[OrganizationsPage.Validators.OrganizationsValidator]
        ] = []
        _next_page_validators: typing.ClassVar[typing.List[OrganizationsPage.Validators.NextPageValidator]] = []

        @classmethod
        def root(
            cls, validator: typing.Callable[[OrganizationsPage.Partial], OrganizationsPage.Partial]
        ) -> typing.Callable[[OrganizationsPage.Partial], OrganizationsPage.Partial]:
            cls._validators.append(validator)
            return validator

        @typing.overload
        @classmethod
        def field(
            cls, field_name: typing_extensions.Literal["organizations"]
        ) -> typing.Callable[
            [OrganizationsPage.Validators.OrganizationsValidator], OrganizationsPage.Validators.OrganizationsValidator
        ]:
            ...

        @typing.overload
        @classmethod
        def field(
            cls, field_name: typing_extensions.Literal["next_page"]
        ) -> typing.Callable[
            [OrganizationsPage.Validators.NextPageValidator], OrganizationsPage.Validators.NextPageValidator
        ]:
            ...

        @classmethod
        def field(cls, field_name: str) -> typing.Any:
            def decorator(validator: typing.Any) -> typing.Any:
                if field_name == "organizations":
                    cls._organizations_validators.append(validator)
                if field_name == "next_page":
                    cls._next_page_validators.append(validator)
                return validator

            return decorator

        class OrganizationsValidator(typing_extensions.Protocol):
            def __call__(
                self, v: typing.List[OrganizationId], *, values: OrganizationsPage.Partial
            ) -> typing.List[OrganizationId]:
                ...

        class NextPageValidator(typing_extensions.Protocol):
            def __call__(self, v: typing.Optional[int], *, values: OrganizationsPage.Partial) -> typing.Optional[int]:
                ...

    @pydantic.root_validator
    def _validate(cls, values: OrganizationsPage.Partial) -> OrganizationsPage.Partial:
        for validator in OrganizationsPage.Validators._validators:
            values = validator(values)
        return values

    @pydantic.validator("organizations")
    def _validate_organizations(
        cls, v: typing.List[OrganizationId], values: OrganizationsPage.Partial
    ) -> typing.List[OrganizationId]:
        for validator in OrganizationsPage.Validators._organizations_validators:
            v = validator(v, values=values)
        return v

    @pydantic.validator("next_page")
    def _validate_next_page(cls, v: typing.Optional[int], values: OrganizationsPage.Partial) -> typing.Optional[int]:
        for validator in OrganizationsPage.Validators._next_page_validators:
            v = validator(v, values=values)
        return v

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Partial(typing_extensions.TypedDict):
        organizations: typing_extensions.NotRequired[typing.List[OrganizationId]]
        next_page: typing_extensions.NotRequired[typing.Optional[int]]

    class Config:
        frozen = True
        allow_population_by_field_name = True
