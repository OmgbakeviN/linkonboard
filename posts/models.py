from django.db import models
from django.conf import settings

# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts_authored")
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    # publier à tout le monde (tous les membres) ?
    is_broadcast = models.BooleanField(default=False)
    # destinataires ciblés (plusieurs murs)
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="posts_received", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]


