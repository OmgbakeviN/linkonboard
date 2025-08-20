from django.contrib import admin
from .models import Submission, Invite
# Register your models here.

admin.site.register(Invite)
admin.site.register(Submission)