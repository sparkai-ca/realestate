from rest_framework.permissions import BasePermission
from .models import Post
# from rest_framework_simplejwt.authentication import JWTAuthentication
# JWT_authenticator = JWTAuthentication()


class IsEmailVerified(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_email_verified:
            return True
        return False


class IsActive(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_active:
            return True
        return False


class IsSelf(BasePermission):
    def has_permission(self, request, view):
        pk = view.kwargs['pk']
        post_userid = Post.objects.get(pk = pk).postuserid.id
        userid = request.user.id
        if str(post_userid) == str(userid):
            return True
        return False

