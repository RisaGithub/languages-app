from django.contrib import admin
from .models import Language, Word, Translation, UserTranslation, ExampleSentencePair


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Language._meta.fields]


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Word._meta.fields]
    search_fields = ("text",)
    list_filter = ("language", "approved")
    ordering = ("-created_at",)


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Translation._meta.fields]
    search_fields = ("text",)
    list_filter = ("language", "approved", "part_of_speech")
    ordering = ("-created_at",)


@admin.register(UserTranslation)
class UserTranslationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserTranslation._meta.fields]
    list_filter = ("user",)

@admin.register(ExampleSentencePair)
class ExampleSentencePairAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ExampleSentencePair._meta.fields]