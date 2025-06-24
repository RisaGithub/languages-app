from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile_and_set_username(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        new_username = str(profile.uuid)

        if instance.username != new_username:
            instance.username = new_username
            # Use update to avoid re-triggering signals
            User.objects.filter(pk=instance.pk).update(username=new_username)
