from fastapi_mason.pagination import PageNumberPagination
from fastapi_mason.types import ModelType
from fastapi_mason.viewsets import GenericViewSet
from fastapi_mason.wrappers import PaginatedResponseDataWrapper, ResponseDataWrapper


class BaseGenericViewSet(GenericViewSet[ModelType]):
    pagination = PageNumberPagination
    list_wrapper = PaginatedResponseDataWrapper
    single_wrapper = ResponseDataWrapper


class BaseViewSet(BaseGenericViewSet[ModelType]):
    pass
