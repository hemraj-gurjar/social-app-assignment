from django.urls import path
from .views import (
    SignupView,
    SearchUserView,
    ListFriendsView,
    PendingFriendRequestsView,
    FriendRequestView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("search/", SearchUserView.as_view(), name="search_users"),
    path(
        "friend-request/send/", FriendRequestView.as_view(), name="send_friend_request"
    ),
    path(
        "friend-request/respond/",
        FriendRequestView.as_view(),
        name="respond_friend_request",
    ),
    path("friends/", ListFriendsView.as_view(), name="list_friends"),
    path(
        "friend-requests/pending/",
        PendingFriendRequestsView.as_view(),
        name="pending_friend_requests",
    ),
]
