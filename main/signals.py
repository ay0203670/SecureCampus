from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UploadedFile

@receiver(post_save, sender=UploadedFile)
def update_user_upload_count(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.profile.upload_count = UploadedFile.objects.filter(user=user).count()
        user.profile.save()