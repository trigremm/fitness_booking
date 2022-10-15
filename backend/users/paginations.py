from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


class UserPagination(LimitOffsetPagination):
    default_limit = 15
