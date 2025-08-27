# accounts/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = getattr(user, "role", "MEMBER")  # claim pour usage serveur
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = getattr(self.user, "role", "MEMBER")  # renvoyé au front
        data["username"] = self.user.username
        data["email"] = self.user.email
        return data
