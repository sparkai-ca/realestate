from rest_framework import (
    status,
    viewsets,
    filters,
    mixins,
    generics,
)
from .permissions import (
    IsAdmin_or_IsSelf,
    IsEmailVerified,
    IsActive,
)
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)
from .serializers import (
    UserCreationSerializer,
    UserSerializer,
    UserChangePasswordSerializer,
    UserSetNewPasswordSerializer,
    UserLogoutSerializer
)
from .models import (
    User,
)
from rest_framework_simplejwt.tokens import (
    RefreshToken,
)
from django.utils.encoding import (
    smart_bytes,
    smart_str,
)
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils import Utils, send_html_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from decouple import config
from django.db import IntegrityError, transaction


class UserViewSet(
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
    serializer_class = UserSerializer
    queryset = User.objects.all()
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
        '$email',
        '$username',
        '$phonenumber',
    ]
    def get_permissions(self):
        print(self.action)
        if self.action in ['list']:
            self.permission_classes = [IsAuthenticated & IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated & IsAdmin_or_IsSelf & IsActive & IsEmailVerified]
        elif self.action in ['retrieve']:
            self.permission_classes = [IsAuthenticated & IsActive & IsEmailVerified]
        elif self.action in ['create']:
            self.permission_classes = [AllowAny]
        elif self.action in ['destroy']:
            self.permission_classes = [IsAuthenticated & IsAdminUser]
        else:
            self.permission_classes = [~AllowAny]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


    def options(self, request, *args, **kwargs):
        self.serializer_class = UserSerializer
        options_result = super().options(request, *args, **kwargs)
        print(options_result)
        return options_result

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        self.serializer_class = UserSerializer
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
        self.serializer_class = UserSerializer
        retrieve_result = super().retrieve(request, *args, **kwargs)
        return retrieve_result

    def create(self, request, *args, **kwargs):
        self.serializer_class = UserCreationSerializer
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = None
            try:
                with transaction.atomic():
                    serializer.save()
                    user_data = serializer.data
                    user = User.objects.get(email=user_data['email'])
                    token = RefreshToken.for_user(user).access_token
                    current_site = get_current_site(request)
                    relative_link = reverse('authentication:verify_email')
                    absurl = 'http://'+str(current_site)+str(relative_link)+"?token="+str(token)
                    emailbody = "Hi "+user.username+", In order to proceed and enjoy all functionalities of RealEstate, " \
                                                    "kindly verify your email address.\n\n" \
                                                    "To verify email go to the link below:\n" \
                                                    "link: "+absurl
                    data = {
                        "domain": absurl,
                        "subject": "Verify you email (realestate)",
                        "body": emailbody,
                        "recepient": [user.email]
                    }
                    Utils.send_email(data)
            except Exception as ex:
                user.delete()
                return Response(data={"error": ["Some error occurred while saving data => "+str(ex)]}, status=status.HTTP_400_BAD_REQUEST)

            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        self.serializer_class = UserSerializer
        update_result = super().update(request, *args, **kwargs)
        return update_result

    def destroy(self, request, *args, **kwargs):
        self.serializer_class = UserSerializer
        destroy_result = super().destroy(request, *args, **kwargs)
        return destroy_result


class UserChangePasswordViewSet(
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
):
    serializer_class = UserChangePasswordSerializer
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()

    def get_permissions(self):
        print(self.action)
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated & IsAdmin_or_IsSelf]
        else:
            self.permission_classes = [~AllowAny]
        return [permission() for permission in self.permission_classes]

    def update(self, request, *args, **kwargs):
        update_result = super().update(request, *args, **kwargs)
        if update_result.status_code == 200:
            request.user.set_password(request.data['new_password'])
            request.user.save()
            return Response(data={"success": ["Password Updated Successfully"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=self.serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class UserVerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        jwt_auth = JWTAuthentication()

        request.META['HTTP_AUTHORIZATION'] = str('Bearer ' + str(str(request.META['QUERY_STRING']).strip()
                                                                 .split('token=')[-1]).strip())
        user, token = jwt_auth.authenticate(request)
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save()
            return Response(data={"success": ["Email Verified Successfully"]}, status=status.HTTP_200_OK)
        return Response(data={"error": ["Email is already verified"]}, status=status.HTTP_400_BAD_REQUEST)


class UserRequestResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    # serializer_class = UserRequestResetEmailSerializer
    def post(self, request, *args, **kwargs):
        # serializer = self.serializer_class(data = request.data)
        email = request.data['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request = request).domain
            relative_link = reverse("authentication:check_reset_password_token", kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://'+current_site + relative_link
            emailbody = "Hello "+user.username+", Use this link below to reset password \nlink: "+str(absurl)
            data = {
                "domain": absurl,
                "subject": "Verify you email (realestate)",
                "body": emailbody,
                "recepient": [user.email]
            }
            Utils.send_email(data)
            return Response(data={"success": ["Request Initiated for Reset Password"]}, status=status.HTTP_200_OK)
        return Response(data={"error": ["No user affiliated with this email"]}, status=status.HTTP_400_BAD_REQUEST)


class UserResetPasswordTokenCheckAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'resetpassword.html'
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id = id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(data={"error": "Token is not valid"}, status=status.HTTP_400_BAD_REQUEST)
            data = {
                    "url": config("URL"),
                    "message": "Credentials are Valid",
                    "uidb64": uidb64,
                    "token": token
                    }
            return Response({"data": data})
        except Exception as ex:
            return Response(data={"error": "Some Error Occured\n"+str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class UserSetNewPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSetNewPasswordSerializer
    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data={"success": "Password reset done successfully"}, status=status.HTTP_200_OK)


class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLogoutSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={"success": "Logout Successfully"}, status=status.HTTP_200_OK)