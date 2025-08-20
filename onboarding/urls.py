from django.urls import path
from .views import InviteCreateAPIView, InviteRetrieveAPIView, SubmissionCreateAPIView

urlpatterns = [
    path("invites/", InviteCreateAPIView.as_view(), name="invite-create"),
    path("invites/<str:token>/", InviteRetrieveAPIView.as_view(), name="invite-detail"),
    path("invites/<str:token>/submit/", SubmissionCreateAPIView.as_view(), name="submission-create"),
]
