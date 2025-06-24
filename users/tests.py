from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from users.models import UserProfile
import uuid


class TestCreateAnonymousUserView(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_anonymous_user(self):
        response = self.client.post("/api/users/create-anonymous/")

        # Check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("user_id", data)
        self.assertIn("uuid", data)

        # Validate the user was actually created
        user = User.objects.get(id=data["user_id"])
        self.assertIsNotNone(user)
        self.assertEqual(user.username, data["uuid"])

        # Validate the associated profile exists
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(str(profile.uuid), data["uuid"])
