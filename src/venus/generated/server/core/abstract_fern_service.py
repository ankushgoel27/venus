# This file was auto-generated by Fern from our API Definition.

# flake8: noqa
# fmt: off
# isort: skip_file

from __future__ import annotations

import abc

import fastapi


class AbstractFernService(abc.ABC):
    @classmethod
    def _init_fern(cls, router: fastapi.APIRouter) -> None:
        ...
