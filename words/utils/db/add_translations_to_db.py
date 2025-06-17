from words.models import ExampleSentencePair
from words.models import Language, Word, Translation


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
