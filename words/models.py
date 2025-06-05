from django.db import models
from django.contrib.auth.models import User


class Word(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.CharField(max_length=100)
	translations_json = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.text} (User {self.user.id})"

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['user', 'text'], name='unique_word_per_user')
		]
