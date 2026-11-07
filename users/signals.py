from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
import users.models as models


@receiver(post_save, sender=models.User)
def create_profile(sender, instance, created, **kwargs):

    if created:
        if instance.role == models.User.Role.CLIENT:
            models.ClientProfile.objects.create(user=instance)
        elif instance.role == models.User.Role.PLAYER:
            models.PlayerProfile.objects.create(user=instance)