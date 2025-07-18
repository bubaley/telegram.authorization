from datetime import datetime

from tortoise.queryset import QuerySet

from app.domains.link.models import Link


def get_active_links() -> QuerySet[Link]:
    return Link.filter(expire_at__gt=datetime.now(), used_at__isnull=True)
