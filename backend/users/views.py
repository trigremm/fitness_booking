import django_filters.rest_framework as filters
from django.db.models import Q
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import User
from .paginations import UserPagination
from .serializers import (
    CurrentUserSerializer,
    UserActivationSerializer,
    UserForgotPasswordSerializer,
    UserRegisterationSerializer,
    UserResetPasswordSerializer,
    UserRetrieveUpdateProfileSerializer,
)


class AnonymousUserViewSet(ViewSet):
    permission_classes = (AllowAny,)

    @extend_schema(
        request=UserRegisterationSerializer,
        responses={201: UserRegisterationSerializer},
        methods=["POST"],
    )
    def user_registration(self, request):
        data = request.data
        serializer = UserRegisterationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response("Email succesifully registered", status=status.HTTP_201_CREATED)
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            return Response({"details": e.args}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=UserActivationSerializer,
        responses={200: UserActivationSerializer},
        methods=["GET"],
    )
    def user_activation(self, request):
        data = request.query_params
        serializer = UserActivationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response("Email succesfully activated", status=status.HTTP_200_OK)
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            return Response({"details": e.args}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=UserForgotPasswordSerializer,
        responses={200: UserForgotPasswordSerializer},
        methods=["POST"],
    )
    def user_forgot_password(self, request):
        data = request.data
        serializer = UserForgotPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response("Email succesfully sent", status=status.HTTP_200_OK)
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            return Response({"details": e.args}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=UserResetPasswordSerializer,
        responses={201: UserResetPasswordSerializer},
        methods=["POST"],
    )
    def user_reset_password(self, request):
        """generate a pasword recovery link and send to email"""
        data = request.data
        serializer = UserResetPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:  # pylint: disable=invalid-name, broad-except
            return Response({"details": e.args}, status=status.HTTP_400_BAD_REQUEST)

    def not_implemented(self, request):  # pylint: disable=unused-argument
        return Response("Not implemented", status=status.HTTP_501_NOT_IMPLEMENTED)


class CurrentUserView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.filter(is_active=True, is_superuser=False)
    serializer_class = CurrentUserSerializer

    def get_object(self):
        return self.request.user


class UserProfileAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.filter(is_active=True, is_superuser=False)
    serializer_class = UserRetrieveUpdateProfileSerializer

    def get_object(self):
        return self.request.user


class UserSearchFilter(filters.FilterSet):
    search = filters.CharFilter(method="filter_search", required=False)

    def filter_search(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                Q(user__first_name__icontains=value)
                | Q(user__last_name__icontains=value)
                | Q(user__email__icontains=value)
            )
        return queryset

    class Meta:
        model = User
        fields = ("search",)


class UserListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.filter(is_active=True)
    serializer_class = CurrentUserSerializer
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name", "email"]

    def get_pagination_class(self):
        if "limit" in self.request.query_params:
            return UserPagination
        return None

    pagination_class = property(fget=get_pagination_class)
