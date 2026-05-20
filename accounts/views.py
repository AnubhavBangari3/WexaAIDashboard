from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    SignupSerializer,
    UserSerializer,
    InviteUserSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class InviteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role not in [User.ROLE_OWNER, User.ROLE_ADMIN]:
            return Response(
                {"detail": "Only Owner/Admin can invite users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.organization:
            return Response(
                {"detail": "Current user has no organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = InviteUserSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)
        invited_user = serializer.save()

        return Response(
            {
                "message": "User invited successfully.",
                "user": UserSerializer(invited_user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class OrganizationUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.filter(organization=request.user.organization)
        return Response(UserSerializer(users, many=True).data)