from rest_framework import serializers
from .models import Invite, Submission

class InviteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ["id", "token", "target_email", "expires_at", "created_at", "status"]
        read_only_fields = ["id", "token", "created_at", "status"]

class InviteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ["token", "status", "expires_at", "target_email", "created_at"]

class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["full_name", "email", "phone", "birth_date", "extra"]

class SubmissionDetailSerializer(serializers.ModelSerializer):
    invite = InviteDetailSerializer()
    class Meta:
        model = Submission
        fields = ["invite", "full_name", "email", "phone", "birth_date", "extra", "created_at"]
