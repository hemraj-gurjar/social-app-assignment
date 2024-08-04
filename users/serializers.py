from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import FriendRequest
from django.core.validators import validate_email

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        extra_kwargs = {
            "email": {
                "validators": [validate_email],
            },
        }


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ["id", "from_user", "timestamp", "accepted"]
