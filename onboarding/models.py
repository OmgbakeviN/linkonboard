from django.db import models
from django.conf import settings
import secrets
# Create your models here.

def gen_token():
    return secrets.token_urlsafe(16)

class Invite(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "PENDING"),
        (STATUS_APPROVED, "APPROVED"),
        (STATUS_REJECTED, "REJECTED"),
    ]
    token = models.CharField(max_length=64, unique=True, default=gen_token)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    target_email = models.EmailField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="invites")
    created_at = models.DateTimeField(auto_now_add=True)

class Submission(models.Model):
    invite = models.OneToOneField(Invite, on_delete=models.CASCADE, related_name="submission")
    full_name = models.CharField(max_length=180)
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    birth_date = models.DateField()
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

