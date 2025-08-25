from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()

class PostCreateSerializer(serializers.ModelSerializer):
    # liste d'ids de membres ciblés (facultatif si is_broadcast=true)
    recipient_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Post
        fields = ["id", "title", "body", "is_broadcast", "recipient_ids", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        is_broadcast = attrs.get("is_broadcast", False)
        rec_ids = self.initial_data.get("recipient_ids") or []
        if not is_broadcast and len(rec_ids) == 0:
            raise serializers.ValidationError("Fournir des destinataires ou activer is_broadcast.")
        return attrs

    def create(self, validated_data):
        rec_ids = self.initial_data.get("recipient_ids") or []
        post = Post.objects.create(
            author=self.context["request"].user,
            title=validated_data.get("title", ""),
            body=validated_data["body"],
            is_broadcast=validated_data.get("is_broadcast", False),
        )
        if not post.is_broadcast and rec_ids:
            qs = User.objects.filter(id__in=rec_ids, role="MEMBER", is_active=True)
            post.recipients.set(qs)
        return post

class PostForMemberSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "body", "author_name", "created_at", "is_broadcast"]

class PostForClientListSerializer(serializers.ModelSerializer):
    recipients_count = serializers.IntegerField(source="recipients.count", read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "body", "is_broadcast", "recipients_count", "created_at"]
