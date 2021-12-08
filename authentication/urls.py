from django.urls import path
from django.conf.urls import include, url
from rest_framework_nested.routers import SimpleRouter
from .views import (
    UserViewSet,
    UserChangePasswordViewSet,
    UserVerifyEmailView,
    UserRequestResetPasswordView,
    UserResetPasswordTokenCheckAPIView,
    UserSetNewPasswordView,
    UserLogoutView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


app_name = 'authentication'

router = SimpleRouter(trailing_slash=False)
router.register("user", UserViewSet)
router.register("changepassword", UserChangePasswordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.was_view(), name='token_refresh'),
    path('verifyemail', UserVerifyEmailView.as_view(), name='verify_email'),
    path('requestresetpassword', UserRequestResetPasswordView.as_view(), name='request_reset_password'),
    path('checkresetpasswordtoken/<uidb64>/<token>', UserResetPasswordTokenCheckAPIView.as_view(), name='check_reset_password_token'),
    path('resetnewpassword', UserSetNewPasswordView.as_view(), name='reset_new_password'),
    path('logout', UserLogoutView.as_view(), name='logout'),
]
