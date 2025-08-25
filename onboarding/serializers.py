from rest_framework import serializers
from .models import Invite, Submission
from django.contrib.auth import get_user_model


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

class SubmissionListItemSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="invite.status", read_only=True)
    token = serializers.CharField(source="invite.token", read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Submission
        fields = ["id", "full_name", "email", "phone", "birth_date", "created_at", "status", "token"]

class DecisionResultSerializer(serializers.Serializer):
    submission_id = serializers.IntegerField()
    invite_status = serializers.CharField()
    created_username = serializers.CharField(allow_null=True)

class MemberWithSubmissionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()
    full_name = serializers.CharField()
    phone = serializers.CharField()
    birth_date = serializers.DateField()
    submission_created_at = serializers.DateTimeField()
    invite_status = serializers.CharField()
    token = serializers.CharField()

