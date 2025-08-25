from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
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
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        post = serializer.save()  # à ce stade, recipients sont déjà set dans create()

        # calcule les destinataires **après** serializer.save()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if post.is_broadcast:
            recipients = User.objects.filter(role="MEMBER", is_active=True)
        else:
            recipients = post.recipients.all()

        notify_post_email(post, recipients)

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

# notify about new post
def notify_post_email(post, recipients):
    # recipients: queryset/list d'objets User (role=MEMBER) avec email
    emails = [u.email for u in recipients if u.email]
    if not emails:
        return
    subject = post.title or "Nouveau message"
    body = (
        f"Vous avez reçu un nouveau message de {post.author.username}.\n\n"
        f"Titre: {post.title or '(sans titre)'}\n"
        f"Contenu:\n{post.body}\n\n"
        f"Connectez-vous pour le lire: {settings.FRONTEND_URL or 'http://localhost:5173'}/wall"
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=True)
    except Exception:
        pass

# gestion des posts
class PostDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsClient]
    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
        except Post.DoesNotExist:
            return Response({"detail":"not_found_or_forbidden"}, status=404)
        post.delete()
        return Response(status=204)

class PostPinToggleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsClient]
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
        except Post.DoesNotExist:
            return Response({"detail":"not_found_or_forbidden"}, status=404)
        post.is_pinned = not post.is_pinned
        post.save(update_fields=["is_pinned"])
        return Response({"id": post.id, "is_pinned": post.is_pinned}, status=200)

