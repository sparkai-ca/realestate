
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from rest_framework_nested.routers import SimpleRouter
from .views import (
    PostViewSet,
    PostsByUserNameViewSet
)

app_name = 'post'
router = SimpleRouter(trailing_slash=False)
router.register("posts", PostViewSet)
router.register("searchposts", PostsByUserNameViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
