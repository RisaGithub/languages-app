from django.db import models
from django.contrib.auth.models import User


class Language(models.Model):
    name = models.CharField(max_length=100)

    iso_639_1 = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        unique=True,
        help_text="Two-letter ISO 639-1 code (e.g., 'en' for English)",
    )
    iso_639_3 = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        unique=True,
        help_text="Three-letter ISO 639-3 code (e.g., 'eng' for English)",
    )

    def __str__(self):
        return f"{self.name} ({self.iso_639_1 or self.iso_639_3})"


class Word(models.Model):
    text = models.CharField(max_length=200)
    language = models.ForeignKey(
        Language, related_name="words", on_delete=models.CASCADE
    )
    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("text", "language")

    def __str__(self):
        return f"{self.text} ({self.language.iso_639_1 or self.language.iso_639_3})"


class Translation(models.Model):
    word = models.ForeignKey(
        Word, related_name="translations", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=200)
    language = models.ForeignKey(
        Language, related_name="translations", on_delete=models.CASCADE
    )
    part_of_speech = models.CharField(max_length=50, null=True, blank=True)
    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("word", "text", "language")

    def __str__(self):
        return f"{self.text} ({self.language.iso_639_1 or self.language.iso_639_3})"


class UserTranslation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    translation = models.ForeignKey(Translation, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "word")

    def __str__(self):
        return f"{self.word.text} for {self.user.username or self.user.id}"
