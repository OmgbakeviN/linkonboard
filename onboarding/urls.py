from django.urls import path
from .views import InviteCreateAPIView, InviteRetrieveAPIView, SubmissionCreateAPIView, SubmissionListAPIView, SubmissionApproveAPIView, SubmissionRejectAPIView, AdminMembersWithFormAPIView

urlpatterns = [
    path("invites/", InviteCreateAPIView.as_view(), name="invite-create"),
    path("invites/<str:token>/", InviteRetrieveAPIView.as_view(), name="invite-detail"),
    path("invites/<str:token>/submit/", SubmissionCreateAPIView.as_view(), name="submission-create"),
    #dashboard client
    path("admin/submissions/", SubmissionListAPIView.as_view(), name="submission-list"),
    path("admin/submissions/<int:pk>/approve/", SubmissionApproveAPIView.as_view(), name="submission-approve"),
    path("admin/submissions/<int:pk>/reject/", SubmissionRejectAPIView.as_view(), name="submission-reject"),
    path("admin/members-with-form/", AdminMembersWithFormAPIView.as_view(), name="admin-members-with-form"),
]
