from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from words.models import Language, Word, Translation
from words.utils.parsers.glosbe import get_glosbe_translations
from words.models import ExampleSentencePair


def get_translations_from_database(word_text, source_lang_code, target_lang_code):
    try:
        source_lang = Language.objects.get(iso_639_1=source_lang_code)
        target_lang = Language.objects.get(iso_639_1=target_lang_code)
    except Language.DoesNotExist:
        return {}

    try:
        word = Word.objects.get(text=word_text, language=source_lang)
    except Word.DoesNotExist:
        return {}

    translations = Translation.objects.filter(word=word, language=target_lang)

    result = {}

    for translation in translations:
        pairs = translation.example_pairs.filter(word=word)

        example_sentence_pairs = []
        for pair in pairs:
            example_sentence_pairs.append(
                {
                    "source_example_sentence": {
                        "text": pair.source_text,
                        "word_start_index": pair.source_word_start_index,
                        "word_end_index": pair.source_word_end_index,
                    },
                    "translated_example_sentence": {
                        "text": pair.translated_text,
                        "word_start_index": pair.translated_word_start_index,
                        "word_end_index": pair.translated_word_end_index,
                    },
                }
            )

        # Group translations by part of speech
        pos = translation.part_of_speech or ""
        if pos not in result:
            result[pos] = []

        result[pos].append(
            {
                "translation": translation.text,
                "popularity": translation.popularity,
                "source_example_sentence": (
                    example_sentence_pairs[0]["source_example_sentence"]
                    if example_sentence_pairs
                    else None
                ),
                "translated_example_sentence": (
                    example_sentence_pairs[0]["translated_example_sentence"]
                    if example_sentence_pairs
                    else None
                ),
            }
        )

    return result


def add_translations_to_database(
    word_text, source_lang_code, target_lang_code, translations_dict
):
    source_lang, _ = Language.objects.get_or_create(
        iso_639_1=source_lang_code, defaults={"name": source_lang_code}
    )
    target_lang, _ = Language.objects.get_or_create(
        iso_639_1=target_lang_code, defaults={"name": target_lang_code}
    )

    word, _ = Word.objects.get_or_create(text=word_text, language=source_lang)

    for part_of_speech, translations in translations_dict.items():
        for translation_data in translations:
            translation, _ = Translation.objects.get_or_create(
                word=word,
                language=target_lang,
                text=translation_data["translation"],
                popularity=translation_data["popularity"],
                defaults={"part_of_speech": part_of_speech},
            )

            source = translation_data.get("source_example_sentence")
            translated = translation_data.get("translated_example_sentence")

            # Only create example pair if both are available
            if source and translated:
                ExampleSentencePair.objects.get_or_create(
                    word=word,
                    translation=translation,
                    source_text=source["text"],
                    source_word_start_index=source["word_start_index"],
                    source_word_end_index=source["word_end_index"],
                    translated_text=translated["text"],
                    translated_word_start_index=translated["word_start_index"],
                    translated_word_end_index=translated["word_end_index"],
                )


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
            translations = get_translations_from_database(
                word, source_language, target_language
            )

            if not translations:
                # Fetch from Glosbe only if translation is missing
                fetched_translations = get_glosbe_translations(
                    word, source_language, target_language
                )
                if fetched_translations:
                    add_translations_to_database(
                        word, source_language, target_language, fetched_translations
                    )
                # Reload to include example pairs (if any were added)
                translations = get_translations_from_database(
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
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
