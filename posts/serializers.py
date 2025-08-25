# posts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, PostImage

User = get_user_model()

# --- DÉFINIR D'ABORD le serializer des images ---
class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ["id", "image", "uploaded_at"]

# --- Création de post (avec images + multi-destinataires) ---
class PostCreateSerializer(serializers.ModelSerializer):
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    images_out = PostImageSerializer(source="images", many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "title", "body",
            "is_broadcast", "recipient_ids",
            "images", "images_out",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "images_out"]

    def _extract_recipient_ids(self):
        """
        Supporte multipart/form-data:
        - plusieurs clés identiques: recipient_ids=3, recipient_ids=5
        - une seule valeur: recipient_ids=3
        - JSON string (rare): recipient_ids="[3,5]"
        - rien: []
        """
        data = self.initial_data
        rec_ids = []

        # 1) multipart: QueryDict-like -> getlist
        if hasattr(data, "getlist"):
            rec_ids = data.getlist("recipient_ids")

        # 2) sinon, clé simple
        if not rec_ids and "recipient_ids" in data:
            rec_ids = data.get("recipient_ids")
            # peut être "3", ["3","5"] ou chaine JSON
            if isinstance(rec_ids, str):
                # tentative JSON
                import json
                try:
                    parsed = json.loads(rec_ids)
                    rec_ids = parsed
                except Exception:
                    rec_ids = [rec_ids]

        # 3) normalisation -> liste d'int
        if rec_ids is None:
            rec_ids = []
        if not isinstance(rec_ids, (list, tuple)):
            rec_ids = [rec_ids]
        norm = []
        for v in rec_ids:
            s = str(v).strip()
            if not s:
                continue
            try:
                norm.append(int(s))
            except ValueError:
                pass
        return norm

    def validate(self, attrs):
        is_broadcast = attrs.get("is_broadcast", False)
        rec_ids = self._extract_recipient_ids()
        # mémoriser pour create()
        self._rec_ids = rec_ids
        if not is_broadcast and len(rec_ids) == 0:
            raise serializers.ValidationError("Fournir des destinataires ou activer is_broadcast.")
        return attrs

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        rec_ids = getattr(self, "_rec_ids", [])

        post = Post.objects.create(
            author=self.context["request"].user,
            title=validated_data.get("title", ""),
            body=validated_data["body"],
            is_broadcast=validated_data.get("is_broadcast", False),
        )

        if not post.is_broadcast and rec_ids:
            qs = User.objects.filter(id__in=rec_ids, role="MEMBER", is_active=True)
            post.recipients.set(qs)

        for img in images:
            PostImage.objects.create(post=post, image=img)
        return post

# --- Lecture pour le MUR MEMBRE (inclut images) ---
class PostForMemberSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    images_out = PostImageSerializer(source="images", many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "title", "body", "author_name",
            "created_at", "is_broadcast", "is_pinned",
            "images_out",
        ]

# --- Liste côté CLIENT (pour “Mes posts”) ---
class PostForClientListSerializer(serializers.ModelSerializer):
    recipients_count = serializers.IntegerField(source="recipients.count", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "title", "body",
            "is_broadcast", "recipients_count",
            "is_pinned", "created_at",
        ]
