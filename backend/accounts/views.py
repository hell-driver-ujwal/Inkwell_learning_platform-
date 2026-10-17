"""Session and account API endpoints."""

from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsAdmin, SessionReady
from accounts.serializers import (
    AccountActionSerializer,
    AdminUserDetailSerializer,
    AdminUserSerializer,
    LoginSerializer,
    PasswordSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    UserSerializer,
)
from accounts.services import administer_account, authenticate_portal, change_password


class SessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "user": UserSerializer(request.user).data
                if request.user.is_authenticated
                else None,
                "csrf_token": get_token(request),
            }
        )


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate_portal(**serializer.validated_data)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return Response({"user": UserSerializer(user).data, "csrf_token": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, SessionReady]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class PasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        change_password(request=request, password=serializer.validated_data["new_password"])
        return Response(UserSerializer(request.user).data)


class UserAdminViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [SessionReady, IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.order_by("full_name")

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return AdminUserSerializer
        return AdminUserDetailSerializer

    search_fields = ["full_name", "email"]
    filterset_fields = ["role", "status"]

    def perform_destroy(self, instance):
        from accounts.services import delete_account

        delete_account(administrator=self.request.user, user=instance)

    @action(detail=True, methods=["post"], url_path="action")
    def account_action(self, request, pk=None):
        user = self.get_object()
        serializer = AccountActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = administer_account(
            administrator=request.user, user_id=user.id, **serializer.validated_data
        )
        return Response(UserSerializer(user).data)
