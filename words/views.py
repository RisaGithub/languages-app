from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model

from words.utils.parsers.glosbe import get_glosbe_translations
from .utils.db.add_translations_to_db import add_translations_to_database
from words.utils.db.get_translations_from_db import get_translations_from_database

User = get_user_model()


class TranslateWordForUserView(APIView):
    def get(self, request):
        user_uuid = request.query_params.get("user_uuid")
        word = request.query_params.get("word")
        source_language = request.query_params.get("source_language")
        target_language = request.query_params.get("target_language")

        if not all([user_uuid, word, source_language, target_language]):
            return Response(
                {
                    "error": "Missing one or more required parameters: user_uuid, word, source_language, target_language."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Try to load translations from DB (uses serializer)
            translations = get_translations_from_database(
                word, source_language, target_language, user_uuid
            )

            if not translations:
                # Fetch from Glosbe
                fetched_translations = get_glosbe_translations(
                    word, source_language, target_language
                )
                if fetched_translations:
                    add_translations_to_database(
                        word, source_language, target_language, fetched_translations
                    )
                    # Retry loading from DB
                    translations = get_translations_from_database(
                        word, source_language, target_language, user_uuid
                    )

            return Response(
                {
                    "word": word,
                    "source_language": source_language,
                    "target_language": target_language,
                    "translations": translations,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
