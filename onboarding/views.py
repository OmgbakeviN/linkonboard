from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Invite, Submission
from .serializers import InviteCreateSerializer, InviteDetailSerializer, SubmissionCreateSerializer, SubmissionDetailSerializer

# Create your views here.

class InviteCreateAPIView(APIView):
    def post(self, request):
        serializer = InviteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite = serializer.save(created_by=request.user)
        out = InviteDetailSerializer(invite).data
        return Response(out, status=status.HTTP_201_CREATED)
    

class InviteRetrieveAPIView(APIView):
    def get(self, request, token):
        try:
            invite = Invite.objects.get(token=token)
        except Invite.DoesNotExist:
            return Response({"detail": "not_found"}, status=404)
        if invite.expires_at and invite.expires_at < timezone.now():
            return Response({"token": token, "status": "EXPIRED"}, status=200)
        data = InviteDetailSerializer(invite).data
        return Response(data, status=200)
    
class SubmissionCreateAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, token):
        try:
            invite = Invite.objects.get(token=token)
        except Invite.DoesNotExist:
            return Response({"detail": "not_found"}, status=404)
        if invite.expires_at and invite.expires_at < timezone.now():
            return Response({"detail": "invite_expired"}, status=400)
        if invite.status != Invite.STATUS_PENDING:
            return Response({"detail": "invalid_status"}, status=400)
        if hasattr(invite, "submission"):
            return Response({"detail": "already_submitted"}, status=409)
        serializer = SubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save(invite=invite)
        out = SubmissionDetailSerializer(submission).data
        return Response(out, status=201)