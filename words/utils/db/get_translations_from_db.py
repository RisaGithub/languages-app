from words.models import ExampleSentencePair
from words.models import Language, Word, Translation


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
