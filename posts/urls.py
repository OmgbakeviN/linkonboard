from django.urls import path
from .views import (
    PostCreateAPIView, MyPostsListAPIView, ClientPostsListAPIView, MemberListAPIView,
    PostDeleteAPIView, PostPinToggleAPIView
)

urlpatterns = [
    path("posts/", PostCreateAPIView.as_view(), name="post-create"),                 # POST (client)
    path("posts/mine/", MyPostsListAPIView.as_view(), name="posts-mine"),           # GET (member)
    path("posts/client/", ClientPostsListAPIView.as_view(), name="posts-client"),   # GET (client)
    path("members/", MemberListAPIView.as_view(), name="members-list"),             # GET (client)
    path("posts/<int:pk>/", PostDeleteAPIView.as_view(), name="post-delete"), # DELETE (member)
    path("posts/<int:pk>/pin/", PostPinToggleAPIView.as_view(), name="post-pin-toggle"), # POST (member)
]
