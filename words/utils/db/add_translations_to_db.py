from words.models import ExampleSentencePair, Language, Word, Translation
from django.db.models import Q


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
            translation_text = translation_data["translation"]
            popularity = translation_data["popularity"]

            # Try to find existing translation first
            translation = Translation.objects.filter(
                word=word,
                language=target_lang,
                text=translation_text,
            ).first()

            if not translation:
                translation = Translation.objects.create(
                    word=word,
                    language=target_lang,
                    text=translation_text,
                    popularity=popularity,
                    part_of_speech=part_of_speech,
                )

            source = translation_data.get("source_example_sentence")
            translated = translation_data.get("translated_example_sentence")

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
