from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLE_CLIENT = "CLIENT"
    ROLE_MEMBER = "MEMBER"
    ROLE_CHOICES = [
        (ROLE_CLIENT, "Client"),
        (ROLE_MEMBER, "Member"),
    ]
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default=ROLE_MEMBER)