from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import FriendRequest, Friend
from .serializers import UserSerializer, FriendRequestSerializer
from social_network.utility import response_with_status

User = get_user_model()


class SignupView(APIView):
    """
    API view to handle user signup.
    """

    def post(self, request):
        """
        Handle POST request to create a new user.
        """
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return response_with_status(
                status.HTTP_400_BAD_REQUEST, "Invalid email format"
            )

        # Check if email already exists
        if User.objects.filter(email__iexact=email).exists():
            return response_with_status(
                status.HTTP_400_BAD_REQUEST, "Email already exists"
            )

        # Check if the password is provided and meets minimum requirements (e.g., length)
        if not password or len(password) < 6:
            return response_with_status(
                status.HTTP_400_BAD_REQUEST,
                "Password must be at least 6 characters long",
            )

        # Create the user
        try:
            user = User.objects.create_user(
                email=email, password=password, username=email
            )
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return response_with_status(
                status.HTTP_201_CREATED,
                "User created successfully",
                {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            )
        except Exception as e:
            return response_with_status(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


class SearchUserView(generics.ListAPIView):
    """
    API view to search for users.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return queryset based on search query.
        """
        query = self.request.query_params.get("query", "")
        if not query:
            return User.objects.none()

        return User.objects.filter(
            Q(email__iexact=query)
            | Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        ).distinct()


class ListFriendsView(generics.ListAPIView):
    """
    API view to list all friends of the authenticated user.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return queryset of the user's friends.
        """
        user = self.request.user
        friends = FriendRequest.objects.filter(
            (Q(from_user=user) | Q(to_user=user)) & Q(accepted=True)
        ).values_list("from_user", "to_user")
        friend_ids = set(sum(friends, ())) - {user.id}
        return User.objects.filter(id__in=friend_ids)


class PendingFriendRequestsView(generics.ListAPIView):
    """
    API view to list all pending friend requests for the authenticated user.
    """

    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return queryset of pending friend requests.
        """
        return FriendRequest.objects.filter(to_user=self.request.user, accepted=False)


class FriendRequestView(APIView):
    """
    API view to handle sending and responding to friend requests.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST request to send a friend request.
        """
        user_id = request.data.get("user_id")
        if not user_id:
            return response_with_status(
                status.HTTP_400_BAD_REQUEST, "user_id is required"
            )

        try:
            to_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return response_with_status(status.HTTP_404_NOT_FOUND, "User not found")

        from_user = request.user

        # Rate limiting: Check if the user has sent more than 3 requests in the past minute
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(
            from_user=from_user, timestamp__gte=one_minute_ago
        ).count()
        if recent_requests >= 3:
            return response_with_status(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "You can only send 3 friend requests per minute",
            )

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return response_with_status(
                status.HTTP_400_BAD_REQUEST, "Friend request already sent"
            )

        friend_request = FriendRequest.objects.create(
            from_user=from_user, to_user=to_user
        )

        return response_with_status(
            status.HTTP_201_CREATED,
            "Friend request sent",
            {"friend_request_id": friend_request.id},
        )

    def put(self, request):
        """
        Handle PUT request to respond to a friend request.
        """
        request_id = request.data.get("request_id")
        if not request_id:
            return response_with_status(
                status.HTTP_400_BAD_REQUEST, "request_id is required"
            )

        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return response_with_status(
                status.HTTP_404_NOT_FOUND, "Friend request not found"
            )

        if request.user != friend_request.to_user:
            return response_with_status(status.HTTP_403_FORBIDDEN, "Permission denied")

        if friend_request.accepted:
            return response_with_status(
                status.HTTP_400_BAD_REQUEST, "Friend request has already been accepted"
            )

        action = request.data.get("action")
        if action == "accept":
            friend_request.accepted = True
            friend_request.save()
            Friend.make_friend(friend_request.from_user, friend_request.to_user)
            return response_with_status(status.HTTP_200_OK, "Friend request accepted")
        elif action == "reject":
            friend_request.delete()
            return response_with_status(status.HTTP_200_OK, "Friend request rejected")
        else:
            return response_with_status(status.HTTP_400_BAD_REQUEST, "Invalid action")
