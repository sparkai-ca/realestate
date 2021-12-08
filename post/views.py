from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import (
    PostSerializer,
)
from rest_framework import (
    status,
    viewsets,
    filters,
    mixins,
    generics,
)
from .models import (
    Post,
)
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)
from .permissions import (
    IsActive,
    IsEmailVerified,
    IsSelf
)
from rest_framework_simplejwt.authentication import JWTAuthentication


class PostViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin
):
    permission_classes = []
    authentication_classes = [
        JWTAuthentication,
    ]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    """
        '^' Starts-with search.
        '=' Exact matches.
        '@' Full-text search. (Currently only supported Django's PostgreSQL backend.)
        '$' Regex search.
    """
    search_fields = [
        '$poststatus',
        '$postmessage',
    ]

    def get_permissions(self):
        print(self.action)
        if self.action in ['list']:
            self.permission_classes = [(IsAuthenticated) | (IsAuthenticated & IsAdminUser)]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [(IsAuthenticated & IsActive & IsEmailVerified & IsSelf) |
                                       (IsAuthenticated & IsAdminUser)]
        elif self.action in ['retrieve']:
            self.permission_classes = [(IsAuthenticated) | (IsAuthenticated & IsAdminUser)]
        elif self.action in ['create']:
            self.permission_classes = [IsAuthenticated & IsActive & IsEmailVerified]
        elif self.action in ['destroy']:
            self.permission_classes = [(IsAuthenticated & IsActive & IsEmailVerified & IsSelf) |
                                       (IsAuthenticated & IsAdminUser)]
        else:
            self.permission_classes = [~AllowAny]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def options(self, request, *args, **kwargs):
        options_result = super().options(request, *args, **kwargs)
        print(options_result)
        return options_result

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))
        return Response({
            "result": data[offset:offset + limit],
            "offset": offset,
            "limit": limit,
            "count": len(data)
        })

    def retrieve(self, request, *args, **kwargs):
        retrieve_result = super().retrieve(request, *args, **kwargs)
        return retrieve_result

    def create(self, request, *args, **kwargs):
        mutable = request.POST._mutable
        if not mutable:
            request.POST._mutable = True
        if 'is_allowed' not in list(dict(request.data).keys()):
            request.data['is_allowed'] = True
        request.data['postuserid'] = request.user.id
        request.data['postusername'] = request.user.username
        create_result = super().create(request, *args, **kwargs)
        return create_result

    def update(self, request, *args, **kwargs):
        update_result = super().update(request, *args, **kwargs)
        return update_result

    def destroy(self, request, *args, **kwargs):
        destroy_result = super().destroy(request, *args, **kwargs)
        return destroy_result


class PostsByUserNameViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    permission_classes = []
    authentication_classes = [
        JWTAuthentication,
    ]
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    """
        '^' Starts-with search.
        '=' Exact matches.
        '@' Full-text search. (Currently only supported Django's PostgreSQL backend.)
        '$' Regex search.
    """
    search_fields = [
        '$poststatus',
        '$postmessage',
    ]

    def get_permissions(self):
        print(self.action)
        if self.action in ['list']:
            self.permission_classes = [(IsAuthenticated) | (IsAuthenticated & IsAdminUser)]
        elif self.action in ['retrieve']:
            self.permission_classes = [(IsAuthenticated) | (IsAuthenticated & IsAdminUser)]
        else:
            self.permission_classes = [~AllowAny]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(postuserid=request.user))
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))
        return Response({
            "result": data[offset:offset + limit],
            "offset": offset,
            "limit": limit,
            "count": len(data)
        })

    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(postusername=kwargs['pk']))
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))
        return Response({
            "result": data[offset:offset + limit],
            "offset": offset,
            "limit": limit,
            "count": len(data)
        })

