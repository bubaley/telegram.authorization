from typing import TYPE_CHECKING

from fastapi_mason.schemas import build_schema
from tortoise.contrib.pydantic import PydanticModel

from app.domains.link.meta import LinkCreateMeta, LinkMeta
from app.domains.link.models import Link

LinkReadSchema = build_schema(Link, meta=LinkMeta)
LinkCreateSchema = build_schema(Link, meta=LinkCreateMeta, exclude_readonly=True)

if TYPE_CHECKING:
    LinkReadSchema = type('LinkReadSchema', (Link, PydanticModel), {})
    LinkCreateSchema = type('LinkCreateSchema', (Link, PydanticModel), {})
