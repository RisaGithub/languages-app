from rest_framework import serializers
from .models import UserTranslation


class UserTranslationSerializer(serializers.ModelSerializer):
    word = serializers.CharField(source="word.text")
    translation = serializers.CharField(source="translation.text")

    class Meta:
        model = UserTranslation
        fields = ["word", "translation", "progress", "created_at"]
