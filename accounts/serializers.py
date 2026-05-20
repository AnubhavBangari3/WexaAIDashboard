from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from organizations.models import Organization

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    organization_id = serializers.IntegerField(source="organization.id", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "organization_id",
            "organization_name",
        ]


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    organization_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "organization_name"]

    @transaction.atomic
    def create(self, validated_data):
        organization_name = validated_data.pop("organization_name")

        organization = Organization.objects.create(name=organization_name)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            organization=organization,
            role=User.ROLE_OWNER,
        )

        return user


class InviteUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=[
            User.ROLE_ADMIN,
            User.ROLE_ANALYST,
            User.ROLE_VIEWER,
        ]
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        default="Temp@12345",
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data):
        request = self.context["request"]

        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data.get("password", "Temp@12345"),
            role=validated_data["role"],
            organization=request.user.organization,
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = UserSerializer(self.user).data

        return data