from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Post
from .serializers import PostCreateSerializer, PostForMemberSerializer, PostForClientListSerializer
from accounts.permissions import IsClient
from onboarding.models import Submission

# Create your views here.

User = get_user_model()

# 1) Client : créer un post (multi-murs ou broadcast)
class PostCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = PostCreateSerializer
    queryset = Post.objects.all()

# 2) Membre : lister MES posts (broadcast ou ciblés)
class MyPostsListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostForMemberSerializer

    def get_queryset(self):
        user = self.request.user
        # safety : membre uniquement
        if getattr(user, "role", "") != "MEMBER":
            return Post.objects.none()
        return Post.objects.filter(
            Q(is_broadcast=True) | Q(recipients=user)
        ).select_related("author").distinct()
    
# 3) Client : lister ses posts (optionnel)
class ClientPostsListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = PostForClientListSerializer

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).prefetch_related("recipients")
    
# 4) Client : lister les MEMBRES disponibles (pour choisir des murs)
class MemberListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = None  # on renvoie du JSON simple

    def list(self, request, *args, **kwargs):
        # on prend les users créés via submissions approuvées
        member_ids = Submission.objects.filter(
            created_user__isnull=False, invite__status="APPROVED"
        ).values_list("created_user_id", flat=True)
        members = User.objects.filter(id__in=member_ids, is_active=True).values("id", "username", "email")
        return Response(list(members), status=200)