from rest_framework.permissions import BasePermission
# from rest_framework_simplejwt.authentication import JWTAuthentication
# JWT_authenticator = JWTAuthentication()


class IsAdmin_or_IsSelf(BasePermission):
    def has_object_permission(self, request, view, object):
        if request.user == object or request.user.is_superuser or request.user.is_staff:
            return True
        return False

class IsEmailVerified(BasePermission):
    def has_object_permission(self, request, view, object):
        if request.user.is_email_verified:
            return True
        return False

class IsActive(BasePermission):
    def has_object_permission(self, request, view, object):
        if request.user.is_active:
            return True
        return False
