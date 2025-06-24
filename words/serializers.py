from rest_framework import serializers
from words.models import UserTranslation, Translation, ExampleSentencePair


class UserTranslationSerializer(serializers.ModelSerializer):
    word = serializers.CharField(source="word.text")
    translation = serializers.CharField(source="translation.text")

    class Meta:
        model = UserTranslation
        fields = ["word", "translation", "progress", "created_at"]


class ExampleSentenceSerializer(serializers.ModelSerializer):
    source_example_sentence = serializers.SerializerMethodField()
    translated_example_sentence = serializers.SerializerMethodField()

    class Meta:
        model = ExampleSentencePair
        fields = ["source_example_sentence", "translated_example_sentence"]

    def get_source_example_sentence(self, obj):
        return {
            "text": obj.source_text,
            "word_start_index": obj.source_word_start_index,
            "word_end_index": obj.source_word_end_index,
        }

    def get_translated_example_sentence(self, obj):
        return {
            "text": obj.translated_text,
            "word_start_index": obj.translated_word_start_index,
            "word_end_index": obj.translated_word_end_index,
        }


class TranslationSerializer(serializers.ModelSerializer):
    example_sentence = serializers.SerializerMethodField()
    added_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Translation
        fields = [
            "text",
            "popularity",
            "example_sentence",
            "part_of_speech",
            "added_by_user",
        ]

    def get_example_sentence(self, obj):
        word = self.context.get("word")
        pair = obj.example_pairs.filter(word=word).first()
        if not pair:
            return None
        return ExampleSentenceSerializer(pair).data

    def get_added_by_user(self, obj):
        word = self.context.get("word")
        user = self.context.get("user")
        if not user or not word:
            return False
        from words.models import UserTranslation  # To avoid circular imports

        return UserTranslation.objects.filter(
            user=user, word=word, translation=obj
        ).exists()
