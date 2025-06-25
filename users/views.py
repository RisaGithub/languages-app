import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import UserProfile
from words.models import Word, Translation, UserTranslation, Language
from django.contrib.auth.models import User
from words.models import UserTranslation
from words.serializers import UserTranslationSerializer


class CreateAnonymousUserView(APIView):
    def post(self, request):
        # Create user with temporary unique username to satisfy constraints
        temp_username = f"temp_{uuid.uuid4().hex[:30]}"
        user = User.objects.create(username=temp_username)
        user.set_unusable_password()
        user.save()  # `post_save` signal runs, creates profile, sets real username

        profile = user.profile  # Created via signal

        return Response(
            {"user_id": user.id, "uuid": str(profile.uuid)},
            status=status.HTTP_201_CREATED,
        )


class AddUserTranslationView(APIView):
    def post(self, request):
        # Query params
        user_uuid = request.query_params.get("uuid")
        word_text = request.query_params.get("word_text")
        translation_text = request.query_params.get("translation_text")
        source_language = request.query_params.get("source_language")
        target_language = request.query_params.get("target_language")

        # Validate input
        missing_fields = []
        for param in [
            "uuid",
            "word_text",
            "translation_text",
            "source_language",
            "target_language",
        ]:
            if not request.query_params.get(param):
                missing_fields.append(param)

        if missing_fields:
            return Response(
                {
                    "error": f"Missing these required query parameters: {', '.join(missing_fields)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get user
            profile = UserProfile.objects.get(uuid=user_uuid)
            user = profile.user

            # Get languages
            source_lang = Language.objects.get(iso_639_1=source_language)
            target_lang = Language.objects.get(iso_639_1=target_language)

            # Get word and translation
            word = Word.objects.get(text=word_text, language=source_lang)
            translation = Translation.objects.get(
                text=translation_text, word=word, language=target_lang
            )

            # Get or create UserTranslation
            user_translation, created = UserTranslation.objects.get_or_create(
                user=user,
                word=word,
                translation=translation,
            )

            return Response(
                {
                    "message": "Translation added to user dictionary.",
                    "created": created,
                    "word": word.text,
                    "translation": translation.text,
                },
                status=status.HTTP_200_OK,
            )

        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Invalid user uuid."}, status=status.HTTP_404_NOT_FOUND
            )
        except Language.DoesNotExist:
            return Response(
                {"error": "Invalid source or target language code."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Word.DoesNotExist:
            return Response(
                {
                    "error": f"Word '{word_text}' not found in source language '{source_language}'."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Translation.DoesNotExist:
            return Response(
                {
                    "error": f"Translation '{translation_text}' not found in target language '{target_language}' for word '{word_text}'."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteUserTranslationView(APIView):
    def delete(self, request):
        # Query params
        user_uuid = request.query_params.get("uuid")
        word_text = request.query_params.get("word_text")
        translation_text = request.query_params.get("translation_text")
        source_language = request.query_params.get("source_language")
        target_language = request.query_params.get("target_language")

        # Validate input
        missing_fields = []
        for param in [
            "uuid",
            "word_text",
            "translation_text",
            "source_language",
            "target_language",
        ]:
            if not request.query_params.get(param):
                missing_fields.append(param)

        if missing_fields:
            return Response(
                {
                    "error": f"Missing these required query parameters: {', '.join(missing_fields)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get user
            profile = UserProfile.objects.get(uuid=user_uuid)
            user = profile.user

            # Get languages
            source_lang = Language.objects.get(iso_639_1=source_language)
            target_lang = Language.objects.get(iso_639_1=target_language)

            # Get word and translation
            word = Word.objects.get(text=word_text, language=source_lang)
            translation = Translation.objects.get(
                text=translation_text, word=word, language=target_lang
            )

            # Get and delete UserTranslation
            user_translation = UserTranslation.objects.get(
                user=user,
                word=word,
                translation=translation,
            )
            user_translation.delete()

            return Response(
                {
                    "message": "Translation removed from user dictionary.",
                    "word": word.text,
                    "translation": translation.text,
                },
                status=status.HTTP_200_OK,
            )

        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Invalid user uuid."}, status=status.HTTP_404_NOT_FOUND
            )
        except Language.DoesNotExist:
            return Response(
                {"error": "Invalid source or target language code."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Word.DoesNotExist:
            return Response(
                {
                    "error": f"Word '{word_text}' not found in source language '{source_language}'."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Translation.DoesNotExist:
            return Response(
                {
                    "error": f"Translation '{translation_text}' not found in target language '{target_language}' for word '{word_text}'."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except UserTranslation.DoesNotExist:
            return Response(
                {"error": "This translation is not saved in the user's dictionary."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserTranslationsByUUID(APIView):
    def get(self, request, uuid):
        try:
            user_profile = UserProfile.objects.get(uuid=uuid)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "User with this UUID was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        translations = UserTranslation.objects.filter(user=user_profile.user)
        serializer = UserTranslationSerializer(translations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTranslationsByUUIDForWord(APIView):
    def get(self, request):
        user_uuid = request.query_params.get("uuid")
        source_language = request.query_params.get("source_language")
        target_language = request.query_params.get("target_language")
        word = request.query_params.get("word")

        if not all([uuid, source_language, target_language, word]):
            return Response(
                {
                    "error": "Missing required parameters: uuid, source_language, target_language, or word."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_profile = UserProfile.objects.get(uuid=user_uuid)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "User with this UUID was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        translations = UserTranslation.objects.filter(
            user=user_profile.user,
            translation__word__language__iso_639_1=source_language,
            translation__language__iso_639_1=target_language,
            word__text__iexact=word,
        )

        serializer = UserTranslationSerializer(translations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
