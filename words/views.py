from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from words.utils.parsers.glosbe import get_glosbe_translations


class TranslateWordView(APIView):
    def get(self, request):
        word = request.query_params.get("word")
        source_language = request.query_params.get("source_language")
        target_language = request.query_params.get("target_language")

        if not word:
            return Response(
                {"error": "Missing 'word' parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not source_language:
            return Response(
                {"error": "Missing 'source_language' parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not target_language:
            return Response(
                {"error": "Missing 'target_language' parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            translations = get_glosbe_translations(
                word, source_language, target_language
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
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
