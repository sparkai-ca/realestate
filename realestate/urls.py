
from django.contrib import admin
from django.urls import path
from django.urls.conf import include


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/post/', include("post.urls")),
]
