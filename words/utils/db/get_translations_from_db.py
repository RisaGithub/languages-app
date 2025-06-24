from django.contrib.auth import get_user_model
from words.models import Language, Word, Translation
from words.serializers import TranslationSerializer

User = get_user_model()


def get_translations_from_database(word_text, source_lang_code, target_lang_code, user_uuid=None):
	try:
		source_lang = Language.objects.get(iso_639_1=source_lang_code)
		target_lang = Language.objects.get(iso_639_1=target_lang_code)
	except Language.DoesNotExist:
		return {}

	try:
		word = Word.objects.get(text=word_text, language=source_lang)
	except Word.DoesNotExist:
		return {}

	user = None
	if user_uuid:
		try:
			user = User.objects.get(profile__uuid=user_uuid)
		except User.DoesNotExist:
			pass  # `user` stays None

	translations = Translation.objects.filter(word=word, language=target_lang)

	result = {}
	for translation in translations:
		serializer = TranslationSerializer(translation, context={"word": word, "user": user})
		pos = translation.part_of_speech or ""
		if pos not in result:
			result[pos] = []
		result[pos].append(serializer.data)

	return result
