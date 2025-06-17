import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import UserProfile
from words.models import Word, Translation, UserTranslation
from django.contrib.auth.models import User


class CreateAnonymousUserView(APIView):
    def post(self, request):
        # Create user with temporary unique username to satisfy constraints
        temp_username = f"temp_{uuid.uuid4().hex[:30]}"
        user = User.objects.create(username=temp_username)
        user.set_unusable_password()
        user.save()  # `post_save` signal runs, creates profile, sets real username

        profile = user.profile  # Created via signal

        return Response(
            {"user_id": user.id, "anonymous_id": str(profile.anonymous_id)},
            status=status.HTTP_201_CREATED,
        )


class AddUserTranslationView(APIView):
    def post(self, request):
        anonymous_id = request.query_params.get("anonymous_id")
        word_text = request.query_params.get("word_text")
        translation_text = request.query_params.get("translation_text")

        # Validate input
        missing_fields = []
        if not anonymous_id:
            missing_fields.append("anonymous_id")
        if not word_text:
            missing_fields.append("word_text")
        if not translation_text:
            missing_fields.append("translation_text")

        if missing_fields:
            return Response(
                {"error": f"Missing these required query parameters: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            profile = UserProfile.objects.get(anonymous_id=anonymous_id)
            user = profile.user

            word = Word.objects.get(text=word_text)
            translation = Translation.objects.get(text=translation_text, word=word)

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
                {"error": "Invalid anonymous_id."}, status=status.HTTP_404_NOT_FOUND
            )
        except Word.DoesNotExist:
            return Response(
                {"error": f"Word '{word_text}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Translation.DoesNotExist:
            return Response(
                {
                    "error": f"Translation '{translation_text}' not found for word '{word_text}'."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
