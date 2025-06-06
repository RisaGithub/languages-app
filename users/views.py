from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import UserProfile

class CreateAnonymousUserView(APIView):
    def post(self, request):
        # Create a new user without username/password
        user = User.objects.create()
        user.set_unusable_password()
        user.save()

        # Create associated UserProfile (if not auto-created via signal)
        profile = UserProfile.objects.create(user=user)

        return Response({
            "user_id": user.id,
            "anonymous_id": str(profile.anonymous_id)
        }, status=status.HTTP_201_CREATED)
