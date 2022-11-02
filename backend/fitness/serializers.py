from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, FitnessHall, FitnessHallAppointments


class FitnessHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessHall
        fields = ("id", "name", "capacity")


class FitnessHallLoadSerializer(serializers.ModelSerializer):
    load = serializers.SerializerMethodField()

    def get_load(self, obj):
        """
        calculate load hourly"""

        return obj.fitnessHall.fitnesshallappointments_set.filter(has_appointment=True).count()

    class Meta:
        model = FitnessHallAppointments
        fields = "__all__"


class FitenessHallAppointmentCreateSerializer(serializers.ModelSerializer):
    """
    data = {
        "fitness_hall": 1,
        "user" :3,
        "appointment": "2021-05-01 13:00:00",
    }
    for i in data:
        s = FitenessHallAppointmentCreateSerializer(data=i)
        s.is_valid(raise_exception=True)
        s.save()
    """

    class Meta:
        model = FitnessHallAppointments
        fields = "__all__"


class FitenessHallAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessHallAppointments
        fields = "__all__"


class UserRegisterationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirmation",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        validated_data["is_active"] = False
        validated_data["is_staff"] = False
        validated_data["is_superuser"] = False
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        validated_data.pop("password_confirmation")
        user = User.objects.create_user(email, password, **validated_data)
        return user


class UserActivationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("token",)

    def validate(self, attrs):
        if User.objects.filter(token=attrs["token"]).exists() is False:
            raise serializers.ValidationError({"Token": "Token not found"})

        return attrs

    def save(self, **kwargs):  # pylint: disable=unused-argument
        # TODO move to model manager
        token = self.validated_data.get("token")
        instance = User.objects.filter(token=token).first()
        instance.is_active = True
        instance.token = ""
        instance.save()
        user_activated_signal.send(sender=instance.__class__, user=instance)
        return instance


class UserForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email"]

    def save(self, **kwargs):  # pylint: disable=unused-argument
        # TODO move to model manager
        email = self.validated_data.get("email")
        instance = User.objects.get(email=email)
        instance.token = instance.generate_token()
        instance.is_active = False
        instance.save()
        user_password_reset_signal.send(sender=instance.__class__, user=instance)
        return instance


class UserResetPasswordSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("token", "password", "password_confirmation")

    def validate(self, attrs):
        if User.objects.filter(token=attrs["token"]).exists() is False:
            raise serializers.ValidationError({"Token": "Token not found"})
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def save(self, **kwargs):  # pylint: disable=unused-argument
        # TODO move to model manager
        token = self.validated_data.get("token")
        password = self.validated_data.get("password")
        instance = User.objects.filter(token=token).first()
        instance.token = ""
        instance.is_active = True
        instance.set_password(password)
        instance.save()
        # user_password_reset_signal.send(sender=instance.__class__, user=instance)
        return instance


# ██████  ██████   ██████  ███████ ██ ██      ███████
# ██   ██ ██   ██ ██    ██ ██      ██ ██      ██
# ██████  ██████  ██    ██ █████   ██ ██      █████
# ██      ██   ██ ██    ██ ██      ██ ██      ██
# ██      ██   ██  ██████  ██      ██ ███████ ███████


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "last_name",
            "first_name",
            "full_name",
        )


class UserRetrieveUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
        )


class PasswordChangeUsingTokenSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["token", "password", "password_confirmation"]

    def validate(self, data):
        queryset = User.objects.filter(token=data.get("token"))
        if queryset.exists() is False:
            raise serializers.ValidationError("Token not found")
        if queryset.count() > 1:
            raise serializers.ValidationError("Multiple tokens found")
        if data["password"] != data["password_confirmation"]:
            raise serializers.ValidationError("passwords do not match")
        data["user"] = queryset.first()
        if default_token_generator.check_token(data["user"], data["token"]) is False:
            raise serializers.ValidationError("Token expired")
        validate_password(data["password"], user=data["user"])
        return data

    def save(self, **kwargs):  # pylint: disable=unused-argument
        user = self.validated_data.get("user")
        password = self.validated_data.get("password")
        return User.objects.user_password_change(user, password)


class UserUpdatePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "old_password",
            "password",
            "password_confirmation",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        user, password = instance, validated_data["password"]
        return User.objects.user_password_change(user, password)
