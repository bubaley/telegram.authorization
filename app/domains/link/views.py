from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from fastapi_mason.decorators import viewset
from fastapi_mason.mixins import CreateMixin, ListMixin

from app.core.encryption.crypto import CryptoManager
from app.core.viewsets import BaseGenericViewSet
from app.domains.link.models import Link
from app.domains.link.schemas import LinkCreateSchema, LinkReadSchema

links_router = APIRouter(prefix='/links', tags=['links'])


@viewset(links_router)
class LinkViewSet(BaseGenericViewSet[Link], ListMixin[Link], CreateMixin[Link]):
    model = Link
    read_schema = LinkReadSchema
    create_schema = LinkCreateSchema

    async def perform_create(self, obj):
        await obj.fetch_related('bot')
        if not obj.bot:
            raise HTTPException(status_code=400, detail='Invalid bot')
        obj.auth_link = f'https://t.me/{obj.bot.username}?start={obj.id}'
        obj.expire_at = datetime.now() + timedelta(seconds=obj.duration)
        if obj.key:
            obj.key = CryptoManager.encrypt(obj.key)
        await obj.save()
        return obj
