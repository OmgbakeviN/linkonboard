from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .models import Invite, Submission
from .serializers import InviteCreateSerializer, InviteDetailSerializer, SubmissionCreateSerializer, SubmissionDetailSerializer, SubmissionListItemSerializer, DecisionResultSerializer, MemberWithSubmissionSerializer
from accounts.permissions import IsClient

import secrets

User = get_user_model()

# Create your views here.

class InviteCreateAPIView(APIView):
    def post(self, request):
        serializer = InviteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite = serializer.save(created_by=request.user)
        out = InviteDetailSerializer(invite).data
        return Response(out, status=status.HTTP_201_CREATED)
    

class InviteRetrieveAPIView(APIView):
    permission_classes = [AllowAny]
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
        # -------- Notification email --------
        try:
            to_email = None
            # si l'invite a été créée par un client connecté, on prend son email
            if invite.created_by and invite.created_by.email:
                to_email = invite.created_by.email
            # sinon fallback vers l'email de notif global
            if not to_email and getattr(settings, "NOTIFY_CLIENT_EMAIL", ""):
                to_email = settings.NOTIFY_CLIENT_EMAIL

            if to_email:
                subject = "Nouvelle demande reçue"
                body = (
                    f"Une nouvelle soumission a été effectuée.\n\n"
                    f"Nom : {submission.full_name}\n"
                    f"Email : {submission.email}\n"
                    f"Téléphone : {submission.phone}\n"
                    f"Date de naissance : {submission.birth_date}\n\n"
                    f"Token d'invitation : {invite.token}\n"
                    f"Statut actuel : {invite.status}\n"
                )
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=True)
        except Exception:
            # éviter de casser l’API si l’email échoue
            pass
        # -----------------------------------

        out = SubmissionDetailSerializer(submission).data
        return Response(out, status=201)
    
class SubmissionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

class SubmissionListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = SubmissionListItemSerializer
    pagination_class = SubmissionPagination
    filter_backends = [OrderingFilter]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Submission.objects.select_related("invite").all()
        status_param = self.request.query_params.get("status")
        if status_param in ["PENDING", "APPROVED", "REJECTED"]:
            qs = qs.filter(invite__status=status_param)
        # optionnel : filtrer par créateur pour multi-clients
        return qs
    
def notify_email(to_email: str, subject: str, body: str):
    if not to_email:
        return
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=True)
    except Exception:
        pass

def create_member_user_from_submission(sub: Submission) -> User:
    """
    Crée (ou récupère) un compte membre pour la soumission acceptée.
    - username: basé sur l’email (ou fallback random)
    - mot de passe temporaire généré (à changer plus tard)
    """
    email = sub.email.lower().strip()
    username = email.split("@")[0] if "@" in email else f"user_{secrets.token_hex(4)}"

    user, created = User.objects.get_or_create(
        email=email,
        defaults={"username": username, "role": "MEMBER", "is_active": True}
    )
    if created:
        temp_password = secrets.token_urlsafe(8)
        user.set_password(temp_password)
        user.save()
        # stocke le mdp temporaire dans extra ? non (sécurité) — on l’envoie seulement par mail.
        # Tu pourras remplacer par un lien "set-password" tokenisé à la Phase 5.
        notify_email(
            to_email=email,
            subject="Votre accès a été créé",
            body=(
                f"Bonjour {sub.full_name},\n\n"
                f"Votre demande a été acceptée. Un compte a été créé pour vous.\n"
                f"Identifiant: {user.username}\n"
                f"Email: {user.email}\n"
                f"Mot de passe temporaire: {temp_password}\n\n"
                f"Merci de vous connecter et de changer votre mot de passe."
            ),
        )
    # si l’utilisateur existait déjà, assure le rôle
    if getattr(user, "role", "") != "MEMBER":
        user.role = "MEMBER"
        user.save(update_fields=["role"])
    return user

class SubmissionApproveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def post(self, request, pk):
        try:
            sub = Submission.objects.select_related("invite").get(pk=pk)
        except Submission.DoesNotExist:
            return Response({"detail": "not_found"}, status=404)

        inv = sub.invite
        if inv.status != Invite.STATUS_PENDING:
            return Response({"detail": "invalid_status"}, status=400)

        # update statut
        inv.status = Invite.STATUS_APPROVED
        inv.save(update_fields=["status"])

        # créer (ou récupérer) le compte membre
        user = create_member_user_from_submission(sub)
        if sub.created_user_id is None:
            sub.created_user = user
            sub.save(update_fields=["created_user"])

        # notifier le client (créateur) et/ou fallback
        to_email = inv.created_by.email if (inv.created_by and inv.created_by.email) else getattr(settings, "NOTIFY_CLIENT_EMAIL", "")
        notify_email(
            to_email=to_email,
            subject="Soumission acceptée",
            body=f"La soumission #{sub.id} ({sub.full_name} - {sub.email}) a été ACCEPTÉE.",
        )

        data = {
            "submission_id": sub.id,
            "invite_status": inv.status,
            "created_username": user.username,
        }
        return Response(DecisionResultSerializer(data).data, status=200)

class SubmissionRejectAPIView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def post(self, request, pk):
        try:
            sub = Submission.objects.select_related("invite").get(pk=pk)
        except Submission.DoesNotExist:
            return Response({"detail": "not_found"}, status=404)

        inv = sub.invite
        if inv.status != Invite.STATUS_PENDING:
            return Response({"detail": "invalid_status"}, status=400)

        inv.status = Invite.STATUS_REJECTED
        inv.save(update_fields=["status"])

        # notifier le client + éventuellement l’invité
        to_email = inv.created_by.email if (inv.created_by and inv.created_by.email) else getattr(settings, "NOTIFY_CLIENT_EMAIL", "")
        notify_email(
            to_email=to_email,
            subject="Soumission refusée",
            body=f"La soumission #{sub.id} ({sub.full_name} - {sub.email}) a été REFUSÉE.",
        )
        # notifier l’invité (optionnel)
        notify_email(
            to_email=sub.email,
            subject="Votre demande a été refusée",
            body=(
                f"Bonjour {sub.full_name},\n\n"
                f"Votre demande a été refusée. Vous pouvez réessayer plus tard."
            ),
        )

        data = {
            "submission_id": sub.id,
            "invite_status": inv.status,
            "created_username": None,
        }
        return Response(DecisionResultSerializer(data).data, status=200)
    
class AdminMembersWithFormAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = MemberWithSubmissionSerializer

    def get_queryset(self):
        # on ne l'utilise pas (on override list), mais DRF le demande
        return Submission.objects.none()

    def list(self, request, *args, **kwargs):
        subs = Submission.objects.select_related("invite", "created_user").all()
        data = []
        for s in subs:
            u = s.created_user
            if not u:  # si pas encore créé (PENDING)
                data.append({
                    "id": None,
                    "username": "",
                    "email": s.email,
                    "role": "PENDING",
                    "full_name": s.full_name,
                    "phone": s.phone,
                    "birth_date": s.birth_date,
                    "submission_created_at": s.created_at,
                    "invite_status": s.invite.status,
                    "token": s.invite.token,
                })
            else:
                data.append({
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "role": u.role,
                    "full_name": s.full_name,
                    "phone": s.phone,
                    "birth_date": s.birth_date,
                    "submission_created_at": s.created_at,
                    "invite_status": s.invite.status,
                    "token": s.invite.token,
                })
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data, status=200)


